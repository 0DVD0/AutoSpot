from pathlib import Path
from scipy.io import loadmat
from datetime import datetime
from collections import Counter
import csv

DATASET_ROOT = Path("/Users/dvd/Downloads")
IMAGE_ROOT = DATASET_ROOT / "image"
LABEL_ROOT = DATASET_ROOT / "label"
NAMES_FILE = DATASET_ROOT / "make_model_name.mat"
AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    AI_SERVICE_ROOT / "data" / "compcars_inventory.csv"
)

def csv_row_convert(item: dict):
    row = item.copy()

    row["years"] =  ";".join(
        str(year)
        for year in item["years"]
    )

    row["suspicious_years"] = ";".join(
        str(year)
        for year in item["suspicious_years"]
    )
    return row

def validate_dataset():
    required_paths = [
        IMAGE_ROOT,
        LABEL_ROOT,
        NAMES_FILE
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"Required dataset path is missing: {path}")
        print(f"found: {path}")

def inspect_name_data():
    data = loadmat(
        NAMES_FILE, squeeze_me=True, struct_as_record=False
    )

    visible_keys = [
        key 
        for key in data
        if not key.startswith("__")
    
    ]
    print(f"Data variables: {visible_keys}")

    make_names = data["make_names"]
    model_names = data["model_names"]

    print(f"Make container type: {type(make_names)}")
    print(f"Make container shape: {make_names.shape}")
    print(f"Model container type: {type(model_names)}")
    print(f"Model container shape: {model_names.shape}")

    print(f"First raw make: {make_names[0]}")
    print(f"First raw model: {model_names[0]}")

    cleaned_make_names = [
        clean_names(value)
        for value in make_names
    ]

    cleaned_models = [
        clean_names(value)
        for value in model_names
    ]

    valid_make_count = sum(
        name is not None
        for name in cleaned_make_names
    )
    valid_models_count = sum(
        name is not None
        for name in cleaned_models
    )

    empty = sum(
        name is None
        for name in cleaned_models
    )

    print(f"Valid makes: {valid_make_count}")
    print(f"Valid models: {valid_models_count}")
    print(f"Empty model positions: {empty}")

    return cleaned_models, cleaned_make_names
 

def get_names_by_id(names: list[str | None], id: int):
    index = id - 1

    if index < 0 or index >= len(names):
        return None

    return names[index] 


def clean_names(value: object):
    if isinstance(value, str):
        clean_value = value.strip()
        if clean_value:
            return clean_value
        return None
    if getattr(value, "size", None) == 0:
        return None

    raise TypeError(f"Usupported name value: {value!r}")

def get_numeric_directories(parent_directory: Path):
    directories = [
        path 
        for path in parent_directory.iterdir()
        if path.is_dir() and path.name.isdigit()
    ]

    return sorted(
        directories, key=lambda path: int(path.name)
    )

def count_images(directory: Path):
    return sum(
        1
        for path in directory.rglob("*.jpg")
        if path.is_file()
    )


def build_inventory(make_names: list[str | None], model_names: list[str | None]):
    inventory = []

    brand_directories = get_numeric_directories(IMAGE_ROOT)

    for brand_directory in brand_directories:
        brand_id = int(brand_directory.name)

        brand_name = get_names_by_id(make_names, brand_id)

        model_directories = get_numeric_directories(brand_directory)

        for model_directory in model_directories:
            model_id = int(model_directory.name)

            model_name = get_names_by_id(model_names, model_id)

            image_count = count_images(model_directory)

            year_data = analyze_years(model_directory)

            label_data = analyze_labels(model_directory)

            inventory.append(
                {
                    "brand_id": brand_id,
                    "model_id": model_id,
                    "brand_name": brand_name,
                    "model_name": model_name,
                    "image_count": image_count,
                    **year_data,
                    **label_data
                }
            )
    return inventory

def analyze_years(model_directory: Path):
    valid_years = []
    invalid_years = []
    unknown_years = 0

    current_year = datetime.now().year

    for year_directory in model_directory.iterdir():
        if not year_directory.is_dir():
            continue

        year_name = year_directory.name

        if year_name == "unknown":
            unknown_years += count_images(year_directory)
            continue

        if not year_name.isdigit():
            invalid_years.append(year_name)
            continue

        numeric_year = int(year_name)

        if 1900 <= numeric_year <= current_year:
            valid_years.append(numeric_year)
        else:
            invalid_years.append(numeric_year)

    return {
        "years": sorted(valid_years),
        "minimum_year": (
            min(valid_years)
            if valid_years
            else None
        ), 
        "maximum_year": (
            max(valid_years)
            if valid_years
            else None
        ),
        "unknown_year_images": unknown_years,
        "suspicious_years": sorted(invalid_years)


    }

def get_label_path(image_path: Path):
    relative_image_path = image_path.relative_to(IMAGE_ROOT)

    relative_label_path = (relative_image_path.with_suffix(".txt"))

    return LABEL_ROOT / relative_label_path

def read_label(image_path: Path):
    label_path = get_label_path(image_path)

    if not label_path.exists():
        return None, "missing"

    lines = [
        line.strip()
        for line in label_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if line.strip()
    ]

    if len(lines) != 3:
        return None, "malformed"

    try: 
        viewpoint = int(lines[0])
        image_type = int(lines[1])

        bounding_box = [
            int(value)
            for value in lines[2].split()
        ] 
    except ValueError:
        return None, "malformed"

    if len(bounding_box) != 4:
        return None, "malformed"

    x_min, y_min, x_max, y_max = bounding_box

    bounding_box_is_valid = (
        x_min >= 0
        and x_max > x_min
        and y_min >= 0
        and y_max > y_min
    )

    if not bounding_box_is_valid:
        return None, "invalid_bounding"

    return {
        "viewpoint": viewpoint,
        "image_type": image_type,
        "bounding_box": bounding_box
    }, None

def analyze_labels(model_directory: Path):
    viewpoints = Counter()

    valid_labels = 0
    missing_labels = 0
    malformed_labels = 0
    invalid_bounding_boxes = 0

    for image_path in model_directory.rglob("*.jpg"):
        annotaion, error = read_label(image_path)

        if error == "missing":
            missing_labels += 1
            continue

        if error == "malformed":
            malformed_labels += 1
            continue

        if error == "invalid_bounding":
            invalid_bounding_boxes += 1
            continue

        valid_labels += 1

        viewpoints[annotaion["viewpoint"]] += 1

    return {
        "valid_labels": valid_labels,
        "missing_labels": missing_labels,
        "malformed_labels": malformed_labels,
        "invalid_bounding_boxes": (
            invalid_bounding_boxes
        ),
        "viewpoint_unknown": viewpoints[-1],
        "viewpoint_1": viewpoints[1],
        "viewpoint_2": viewpoints[2],
        "viewpoint_3": viewpoints[3],
        "viewpoint_4": viewpoints[4],
        "viewpoint_5": viewpoints[5],
    }


def write_inventory_csv(inventory: list[dict], output_file: Path):
    field_names = [
        "brand_id",
        "model_id",
        "brand_name",
        "model_name",
        "image_count",
        "years",
        "minimum_year",
        "maximum_year",
        "unknown_year_images",
        "suspicious_years",
        "valid_labels",
        "missing_labels",
        "malformed_labels",
        "invalid_bounding_boxes",
        "viewpoint_unknown",
        "viewpoint_1",
        "viewpoint_2",
        "viewpoint_3",
        "viewpoint_4",
        "viewpoint_5",
        ]

    output_file.parent.mkdir(
         parents=True,
         exist_ok=True
     )

    with output_file.open(
         "w", encoding="utf-8", newline=""
     ) as csv_file:
         writer = csv.DictWriter(csv_file, fieldnames=field_names)

         writer.writeheader()

         for item in inventory:
             row = csv_row_convert(item)
             writer.writerow(row)

    print(f"CSV file: {output_file}")

def main():
    print("Start dataset analys...")
    validate_dataset()
    models, makes = inspect_name_data()

    inventory = build_inventory(makes, models)

    write_inventory_csv(inventory, OUTPUT_FILE)

    total_images = sum(
        item["image_count"]
        for item in inventory
    )

    total_valid_labels = sum(
    item["valid_labels"]
    for item in inventory
    )

    total_missing_labels = sum(
        item["missing_labels"]
        for item in inventory
    )

    total_malformed_labels = sum(
        item["malformed_labels"]
        for item in inventory
    )

    total_invalid_bounding_boxes = sum(
        item["invalid_bounding_boxes"]
        for item in inventory
    )

    print(
    f"Valid labels: {total_valid_labels}"
    )

    print(
        f"Missing labels: {total_missing_labels}"
    )

    print(
        f"Malformed labels: "
        f"{total_malformed_labels}"
    )

    print(
        f"Invalid bounding boxes: "
        f"{total_invalid_bounding_boxes}"
    )

    for viewpoint in [
        "viewpoint_unknown",
        "viewpoint_1",
        "viewpoint_2",
        "viewpoint_3",
        "viewpoint_4",
        "viewpoint_5",
        ]:
            total = sum(
                item[viewpoint]
                for item in inventory
            )

            print(f"{viewpoint}: {total}")

    print(f"Inventory models: {len(inventory)}")
    print(f"Inventory images: {total_images}")

    print("First five inventory records:")

    for item in inventory[:5]:
        print(item)

if __name__ == "__main__":
    main()
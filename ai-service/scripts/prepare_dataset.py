import csv
import random
from collections import Counter
from pathlib import Path

DATASET_ROOT = Path("/Users/dvd/Downloads")
IMAGE_ROOT = DATASET_ROOT / "image"
LABEL_ROOT = DATASET_ROOT / "label"

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

SELECTED_CLASSES_FILE = (
    AI_SERVICE_ROOT / "data" / "selected_classes.csv"
)

SPLITS_DIRECTORY = (
    AI_SERVICE_ROOT / "data" / "splits"
)

TRAIN_FILE = SPLITS_DIRECTORY / "train.csv"
VALIDATION_FILE = SPLITS_DIRECTORY / "validation.csv"
TEST_FILE = SPLITS_DIRECTORY / "test.csv"

RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15

def load_selected_classes():
    if not SELECTED_CLASSES_FILE.exists():
        raise FileNotFoundError(
            f"Selected classes file is missing: "
            f"{SELECTED_CLASSES_FILE}"
        )

    with SELECTED_CLASSES_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as selected_file:
        reader = csv.DictReader(selected_file)
        rows = list(reader)

    if not rows:
        raise ValueError("No selected classes were found")

    return rows

def get_label_path(image_path: Path):
    relative_path = image_path.relative_to(
        IMAGE_ROOT
    )

    return (
        LABEL_ROOT
        / relative_path.with_suffix(".txt")
    )

def read_label(label_path: Path):
    if not label_path.exists():
        return None, "missing_label"

    lines = [
        line.strip()
        for line in label_path.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()
        if line.strip()
    ]

    if len(lines) != 3:
        return None, "malformed_label"

    try:
        viewpoint = int(lines[0])
        image_type = int(lines[1])

        bounding_box = [
            int(value)
            for value in lines[2].split()
        ]
    except ValueError:
        return None, "malformed_label"

    if len(bounding_box) != 4:
        return None, "malformed_label"

    x_min, y_min, x_max, y_max = bounding_box

    bounding_box_is_valid = (
        x_min >= 0
        and y_min >= 0
        and x_max > x_min
        and y_max > y_min
    )

    if not bounding_box_is_valid:
        return None, "invalid_bounding_box"

    return {
        "viewpoint": viewpoint,
        "image_type": image_type,
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
    }, None

def build_class_records(class_row: dict):
    class_index = int(class_row["class_index"])
    brand_id = int(class_row["brand_id"])
    model_id = int(class_row["model_id"])

    class_directory = (
        IMAGE_ROOT
        / str(brand_id)
        / str(model_id)
    )

    if not class_directory.exists():
        raise FileNotFoundError(
            f"Class directory is missing: "
            f"{class_directory}"
        )

    records = []
    errors = Counter()

    image_paths = sorted(
        class_directory.rglob("*.jpg")
    )

    for image_path in image_paths:
        label_path = get_label_path(image_path)

        label, error = read_label(label_path)

        if error is not None:
            errors[error] += 1
            continue

        relative_image_path = (
            image_path
            .relative_to(IMAGE_ROOT)
            .as_posix()
        )

        records.append(
            {
                "relative_image_path": (
                    relative_image_path
                ),
                "class_index": class_index,
                "brand": class_row[
                    "normalized_brand"
                ],
                "model": class_row[
                    "normalized_model"
                ],
                "brand_id": brand_id,
                "model_id": model_id,
                "year": image_path.parent.name,
                "viewpoint": label["viewpoint"],
                "image_type": label["image_type"],
                "x_min": label["x_min"],
                "y_min": label["y_min"],
                "x_max": label["x_max"],
                "y_max": label["y_max"],
            }
        )

    return records, errors

def split_class_records(records: list[dict], class_index: int):
    shuffled_records = records.copy()

    class_random = random.Random(RANDOM_SEED + class_index)

    class_random.shuffle(shuffled_records)

    record_count = len(shuffled_records)

    train_count = int(record_count * TRAIN_RATIO)

    validation_count = int(record_count * VALIDATION_RATIO)

    validation_end = (train_count + validation_count)

    train_records = shuffled_records[:train_count]

    validation_records = shuffled_records[train_count:validation_end]

    test_records = shuffled_records[validation_end:]

    if (not train_records or not validation_records or not test_records):
        raise ValueError(f"Class {class_index} cannot be split"
                         f"{record_count} records")

    return (train_records, validation_records, test_records)


def write_manifest(output_file: Path, records: list[dict]):
    field_names = [
        "relative_image_path",
        "class_index",
        "brand",
        "model",
        "brand_id",
        "model_id",
        "year",
        "viewpoint",
        "image_type",
        "x_min",
        "y_min",
        "x_max",
        "y_max",
    ]

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as manifest_file:
        writer = csv.DictWriter(
            manifest_file,
            fieldnames=field_names,
        )

        writer.writeheader()
        writer.writerows(records)

    print(
        f"{output_file.name}: "
        f"{len(records)} records"
    )

def validate_splits(train_records: list[dict], validation_records: list[dict], test_records: list[dict]):
    train_paths = {
        row["relative_image_path"]
        for row in train_records
    }

    validation_paths = {
        row["relative_image_path"]
        for row in validation_records
    }  

    test_paths = {
        row["relative_image_path"]
        for row in test_records
    }

    if train_paths & validation_paths:
        raise ValueError("Train and validation overlap")

    if train_paths & test_paths:
        raise ValueError("Train and test overlap")

    if validation_paths & test_paths:
        raise ValueError("Validation and train overlap")

    all_records_count = (len(validation_records) + len(train_records) + len(test_records))

    path_count = len(train_paths | validation_paths | test_paths)

    if all_records_count != path_count:
        raise ValueError("Duplicate image paths exist")

    print("Splits validated")
    print(f"Uniques images: {path_count}")

def main():
    print("Preparing AutoSpot dataset...")

    selected_classes = load_selected_classes()

    train_records = []
    validation_records = []
    test_records = []

    total_errors = Counter()

    for class_row in selected_classes:
        class_index = int(
            class_row["class_index"]
        )

        class_records, class_errors = (
            build_class_records(class_row)
        )

        total_errors.update(class_errors)

        (class_train, class_validation, class_test) = split_class_records(class_records, class_index)

        train_records.extend(class_train)
        validation_records.extend(class_validation)
        test_records.extend(class_test)

    validate_splits(train_records, validation_records, test_records)

    write_manifest(TRAIN_FILE, train_records)

    write_manifest(VALIDATION_FILE, validation_records)

    write_manifest(TEST_FILE, test_records)

    print(f"Selected classes: {len(selected_classes)}")
    print(f"Skipped records: {sum(total_errors.values())}")

    for error_name, error_count in sorted(
        total_errors.items()
    ):
        print(f"{error_name}: {error_count}")

    print("Dataset preparation completed")


if __name__ == "__main__":
    main()
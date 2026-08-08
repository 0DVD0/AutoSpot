import csv
import json
from pathlib import Path

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

INVENTORY_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "compcars_inventory.csv"
)

CONFIG_FILE = (
    
    AI_SERVICE_ROOT
    / "data"
    / "selection_config.json"
)

SELECTED_CLASSES_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "selected_classes.csv"
)

CLASS_MAPPING_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "class_mapping.json"
)

def load_config():
    with CONFIG_FILE.open(
        "r", encoding="utf-8"
    ) as config_file:
        return json.load(config_file)

def load_inventory():
    with INVENTORY_FILE.open(
        "r", encoding="utf-8", newline=""
    ) as inventory_file:
        reader = csv.DictReader(inventory_file)
        return list(reader)

def normalize_model_name(raw_brand: str, normalized_brand:str, raw_model: str):
    possible_prefixes = [
        raw_brand,
        normalized_brand
    ]

    for prefix in possible_prefixes:
        expected_prefix = f"{prefix}"

        if raw_model.lower().startswith(expected_prefix.lower()):
            return raw_model[len(expected_prefix):].strip()

    return raw_model.strip()

def select_classes(inventory: list[dict], config: dict):
    minimum_images = config["minimum_images_per_class"]

    excluded_brands = set(config["excluded_regional_brands"] + config["excluded_abstract_brands"])

    name_corrections = config["brand_name_corrections"]

    selected_classes = []

    for row in inventory:
        raw_brand = row["brand_name"]
        image_count = int(row["image_count"])

        if image_count < minimum_images:
            continue

        if raw_brand in excluded_brands:
            continue

        normalized_brand = name_corrections.get(raw_brand, raw_brand)

        raw_model = row["model_name"]

        normalized_model = normalize_model_name(raw_brand, normalized_brand, raw_model)


        selected_row = row.copy()

        selected_row["normalized_brand"] = (normalized_brand)
        selected_row["normalized_model"] = (normalized_model)
        
        selected_classes.append(selected_row)


    selected_classes.sort(
        key= lambda row: (row["normalized_brand"].lower(), row["normalized_model"].lower(), int(row["brand_id"]), int(row["model_id"]))
    )
    for class_index, row in enumerate(selected_classes):
        row["class_index"] = class_index
    return selected_classes

def write_selected_classes(selected_classes: list[dict]):
    if not selected_classes:
        raise ValueError("No classes were selected")

    field_names = [
        "class_index",
        "brand_id",
        "model_id",
        "brand_name",
        "model_name",
        "normalized_brand",
        "normalized_model",
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

    with SELECTED_CLASSES_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as selected_file:
        writer = csv.DictWriter(
            selected_file,
            fieldnames=field_names,
        )

        writer.writeheader()
        writer.writerows(selected_classes)

    print(
        f"Selected classes written to: "
        f"{SELECTED_CLASSES_FILE}"
    )

def write_class_mapping(
    selected_classes: list[dict],
) -> None:
    class_mapping = {}

    for row in selected_classes:
        class_index = str(row["class_index"])

        class_mapping[class_index] = {
            "brand_id": int(row["brand_id"]),
            "model_id": int(row["model_id"]),
            "brand": row["normalized_brand"],
            "model": row["normalized_model"],
        }

    with CLASS_MAPPING_FILE.open(
        "w",
        encoding="utf-8",
    ) as mapping_file:
        json.dump(
            class_mapping,
            mapping_file,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"Class mapping written to: "
        f"{CLASS_MAPPING_FILE}"
    )

def main():
    config = load_config()
    inventory = load_inventory()

    selected_classes = select_classes(inventory, config)

    write_selected_classes(selected_classes)
    write_class_mapping(selected_classes)

    selected_images = sum(
        int(row["image_count"])
        for row in selected_classes
        )

    raw_brands = {
        row["brand_name"]
        for row in selected_classes
    }

    normalized_brands = {
        row["normalized_brand"]
        for row in selected_classes
    }

    print(f"Original classes: {len(inventory)}")

    print(
        f"Selected classes: "
          f"{len(selected_classes)}"
          )

    print(f"Selected images: {selected_images}")
    print(f"Raw brands: {len(raw_brands)}")
    print(f"Normalized brands:"
          f"{len(normalized_brands)}")


if __name__ == "__main__":
    main()
from pathlib import Path
from time import perf_counter

from app.dataset import CarDataSet
from app.transform import evaluation_transforms


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

SPLIT_FILES = {
    "train": (
        AI_SERVICE_ROOT
        / "data"
        / "splits"
        / "train.csv"
    ),
    "validation": (
        AI_SERVICE_ROOT
        / "data"
        / "splits"
        / "validation.csv"
    ),
    "test": (
        AI_SERVICE_ROOT
        / "data"
        / "splits"
        / "test.csv"
    ),
}

EXPECTED_IMAGE_SHAPE = (3, 224, 224)
CLASS_COUNT = 868

def validate_split(
    split_name: str,
    manifest_file: Path,
):
    dataset = CarDataSet(
        manifest_file=manifest_file,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    errors = []

    print(
        f"Validating {split_name}: "
        f"{len(dataset)} images"
    )

    for index in range(len(dataset)):
        try:
            image, label = dataset[index]

            if tuple(image.shape) != EXPECTED_IMAGE_SHAPE:
                raise ValueError(
                    f"Unexpected image shape: "
                    f"{tuple(image.shape)}"
                )

            if not 0 <= label < CLASS_COUNT:
                raise ValueError(
                    f"Invalid class index: {label}"
                )

        except Exception as error:
            record = dataset.reccords[index]

            errors.append(
                {
                    "index": index,
                    "image": record[
                        "relative_image_path"
                    ],
                    "error": str(error),
                }
            )

        if (index + 1) % 5000 == 0:
            print(
                f"  {index + 1}/"
                f"{len(dataset)} checked"
            )

    return len(dataset), errors

def main():
    start_time = perf_counter()

    total_images = 0
    total_errors = 0

    for split_name, manifest_file in (
        SPLIT_FILES.items()
    ):
        image_count, errors = validate_split(
            split_name,
            manifest_file,
        )

        total_images += image_count
        total_errors += len(errors)

        if errors:
            print(
                f"{split_name} errors: "
                f"{len(errors)}"
            )

            for error in errors[:20]:
                print(
                    f"  index={error['index']} "
                    f"image={error['image']} "
                    f"error={error['error']}"
                )
        else:
            print(
                f"{split_name}: no errors"
            )

    elapsed_seconds = (
        perf_counter() - start_time
    )

    print()
    print(f"Checked images: {total_images}")
    print(f"Total errors: {total_errors}")
    print(
        f"Elapsed time: "
        f"{elapsed_seconds:.1f} seconds"
    )

    if total_errors:
        raise RuntimeError(
            "Dataset validation failed"
        )

    print("Dataset validation passed")


if __name__ == "__main__":
    main()
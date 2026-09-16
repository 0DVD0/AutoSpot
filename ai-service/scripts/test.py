from pathlib import Path

from app.dataset import CarDataSet
from app.transform import (evaluation_transforms, train_transform)


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

TRAIN_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "train.csv"
)

VALIDATION_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "validation.csv"
)


def main():
    train_dataset = CarDataSet(
        manifest_file=TRAIN_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=train_transform,
    )

    validation_dataset = CarDataSet(
        manifest_file=VALIDATION_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    train_image, train_label = train_dataset[0]

    validation_image, validation_label = (
        validation_dataset[0]
    )

    print(f"Train records: {len(train_dataset)}")
    print(
        f"Validation records: "
        f"{len(validation_dataset)}"
    )

    print(
        f"Train tensor shape: "
        f"{train_image.shape}"
    )

    print(f"Train label: {train_label}")

    print(
        f"Validation tensor shape: "
        f"{validation_image.shape}"
    )

    print(
        f"Validation label: "
        f"{validation_label}"
    )


if __name__ == "__main__":
    main()
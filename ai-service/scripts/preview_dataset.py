import random
from pathlib import Path

import matplotlib.pyplot as plt
import torch

from app.dataset import CarDataSet
from app.transform import (
    evaluation_transforms,
    train_transform,
)


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

TRAIN_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "train.csv"
)

PREVIEW_DIRECTORY = (
    AI_SERVICE_ROOT
    / "data"
    / "previews"
)

PREVIEW_FILE = (
    PREVIEW_DIRECTORY
    / "dataset_preview.png"
)

IMAGENET_MEAN = torch.tensor(
    [0.485, 0.456, 0.406]
).view(3, 1, 1)

IMAGENET_STANDARD_DEVIATION = torch.tensor(
    [0.229, 0.224, 0.225]
).view(3, 1, 1)

def prepare_image_for_display(image_tensor: torch.Tensor):
    image = (
        image_tensor
        * IMAGENET_STANDARD_DEVIATION
        + IMAGENET_MEAN
    )

    image = image.clamp(0, 1)

    return image.permute(1, 2, 0).numpy()

def main():
    evaluation_dataset = CarDataSet(
        manifest_file=TRAIN_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    augmented_dataset = CarDataSet(
        manifest_file=TRAIN_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=train_transform,
    )

    random_generator = random.Random(42)

    selected_indices = random_generator.sample(
        range(len(evaluation_dataset)),
        8,
    )

    figure, axes = plt.subplots(
        nrows=8,
        ncols=2,
        figsize=(10, 28),
    )

    for row_index, dataset_index in enumerate(
        selected_indices
    ):
        evaluation_image, label = (
            evaluation_dataset[dataset_index]
        )

        augmented_image, _ = (
            augmented_dataset[dataset_index]
        )

        record = evaluation_dataset.reccords[
            dataset_index
        ]

        title = (
            f"{record['brand']} "
            f"{record['model']}\n"
            f"class={label}, "
            f"year={record['year']}"
        )

        axes[row_index][0].imshow(
            prepare_image_for_display(
                evaluation_image
            )
        )

        axes[row_index][0].set_title(
            f"Evaluation\n{title}"
        )

        axes[row_index][0].axis("off")

        axes[row_index][1].imshow(
            prepare_image_for_display(
                augmented_image
            )
        )

        axes[row_index][1].set_title(
            f"Augmented\n{title}"
        )

        axes[row_index][1].axis("off")

    figure.tight_layout()

    PREVIEW_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        PREVIEW_FILE,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close(figure)

    print(
        f"Preview saved to: {PREVIEW_FILE}"
    )


if __name__ == "__main__":
    main()
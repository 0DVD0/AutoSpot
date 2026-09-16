from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader

from app.dataset import CarDataSet
from app.model import create_efficientnet_b0
from app.transform import train_transform


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

TRAIN_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "train.csv"
)

CLASS_COUNT = 868
BATCH_SIZE = 16
TRAINING_STEPS = 10
LEARNING_RATE = 0.001

def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")

def main():
    torch.manual_seed(42)

    device = get_device()

    print(f"Device: {device}")

    train_dataset = CarDataSet(
        manifest_file=TRAIN_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=train_transform,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    images, labels = next(iter(train_loader))

    images = images.to(device)
    labels = labels.to(device)

    print(f"Image batch: {images.shape}")
    print(f"Label batch: {labels.shape}")

    model = create_efficientnet_b0(
        class_count=CLASS_COUNT,
        freeze_backbone=True,
    )

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.AdamW(
        model.classifier.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.0001,
    )

    initial_weights = (
        model.classifier[1]
        .weight
        .detach()
        .clone()
    )

    model.train()

    model.features.eval()

    losses = []

    for step in range(TRAINING_STEPS):
        optimizer.zero_grad(
            set_to_none=True
        )

        outputs = model(images)

        loss = criterion(
            outputs,
            labels,
        )

        if not torch.isfinite(loss):
            raise ValueError(
                f"Loss is not finite: {loss.item()}"
            )

        loss.backward()

        optimizer.step()

        loss_value = loss.item()
        losses.append(loss_value)

        print(
            f"Step {step + 1}/"
            f"{TRAINING_STEPS}, "
            f"loss={loss_value:.4f}"
        )

    final_weights = (
        model.classifier[1]
        .weight
        .detach()
    )

    weights_changed = not torch.equal(
        initial_weights,
        final_weights,
    )

    if not weights_changed:
        raise RuntimeError(
            "Classifier weights did not change"
        )

    print()
    print(f"Initial loss: {losses[0]:.4f}")
    print(f"Final loss: {losses[-1]:.4f}")
    print("Classifier weights changed")
    print("Training smoke test passed")

if __name__ == "__main__":
    main()
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from app.transform import evaluation_transforms
from app.dataset import CarDataSet
from app.model import create_efficientnet_b0

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

VALIDATION_MANIFEST = (AI_SERVICE_ROOT / "data" / "splits" / "validation.csv")

CLASS_COUNT = 868

BATCH_SIZE = 4


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")

def count_parameters(model):
    total_param = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable_param = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return(
        total_param, trainable_param
    )

def main():
    device = get_device()

    print(f"Device: {device}")

    validation_dataset = CarDataSet(
        manifest_file=VALIDATION_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    images, labels = next(
        iter(validation_loader)
    )

    print(f"Input shape: {images.shape}")
    print(f"Label shape: {labels.shape}")

    model = create_efficientnet_b0(
        class_count=CLASS_COUNT,
        freeze_backbone=True,
    )

    model = model.to(device)
    images = images.to(device)

    model.eval()

    with torch.inference_mode():
        outputs = model(images)

    total_parameters, trainable_parameters = (
        count_parameters(model)
    )

    print(f"Output shape: {outputs.shape}")

    print(
        f"Total parameters: "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters: "
        f"{trainable_parameters:,}"
    )

    if tuple(outputs.shape) != (
        BATCH_SIZE,
        CLASS_COUNT,
    ):
        raise ValueError(
            f"Unexpected output shape: "
            f"{tuple(outputs.shape)}"
        )

    print("Model test passed")


if __name__ == "__main__":
    main()
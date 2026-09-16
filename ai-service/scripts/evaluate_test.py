from json import dumps
from pathlib import Path
from time import perf_counter

import torch
from torch import nn
from torch.utils.data import DataLoader

from app.dataset import CarDataSet
from app.model import create_efficientnet_b0
from app.transform import evaluation_transforms


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

TEST_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "test.csv"
)

CHECKPOINT_FILE = (
    AI_SERVICE_ROOT
    / "models"
    / "efficientnet_b0_phase3_best.pt"
)

RESULTS_FILE = (
    AI_SERVICE_ROOT
    / "models"
    / "efficientnet_b0_phase3_test_results.json"
)

CLASS_COUNT = 868
BATCH_SIZE = 32
NUM_WORKERS = 2


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def validate_configuration():
    required_paths = [
        IMAGE_ROOT,
        TEST_MANIFEST,
        CHECKPOINT_FILE,
    ]

    for required_path in required_paths:
        if not required_path.exists():
            raise FileNotFoundError(
                f"Required path is missing: "
                f"{required_path}"
            )

    if CLASS_COUNT <= 0:
        raise ValueError(
            "Class count must be positive"
        )

    if BATCH_SIZE <= 0:
        raise ValueError(
            "Batch size must be positive"
        )

    if NUM_WORKERS < 0:
        raise ValueError(
            "Number of workers cannot be negative"
        )


def load_model(device: torch.device):
    checkpoint = torch.load(
        CHECKPOINT_FILE,
        map_location="cpu",
    )

    if checkpoint["architecture"] != "efficientnet_b0":
        raise ValueError(
            "Unexpected model architecture"
        )

    if checkpoint["phase"] != 3:
        raise ValueError(
            "Expected a phase 3 checkpoint"
        )

    if checkpoint["class_count"] != CLASS_COUNT:
        raise ValueError(
            "Checkpoint class count does not match"
        )

    if checkpoint["dry_run"]:
        raise ValueError(
            "A dry-run checkpoint cannot be "
            "used for final testing"
        )

    model = create_efficientnet_b0(
        class_count=CLASS_COUNT,
        freeze_backbone=True,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = model.to(device)

    model.eval()

    return model, checkpoint


def count_correct_predictions(
    outputs: torch.Tensor,
    labels: torch.Tensor,
):
    predictions = outputs.topk(
        k=3,
        dim=1,
    ).indices

    top_1_correct = (
        predictions[:, 0]
        .eq(labels)
        .sum()
        .item()
    )

    top_3_correct = (
        predictions
        .eq(labels.unsqueeze(1))
        .any(dim=1)
        .sum()
        .item()
    )

    return top_1_correct, top_3_correct


def save_results(results: dict):
    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = RESULTS_FILE.with_suffix(
        ".tmp"
    )

    temporary_file.write_text(
        dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_file.replace(
        RESULTS_FILE
    )


def main():
    validate_configuration()

    device = get_device()

    test_dataset = CarDataSet(
        manifest_file=TEST_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        persistent_workers=(
            NUM_WORKERS > 0
        ),
    )

    model, checkpoint = load_model(device)

    criterion = nn.CrossEntropyLoss(
        label_smoothing=0.1
    )

    total_loss = 0.0
    total_samples = 0

    total_top_1_correct = 0
    total_top_3_correct = 0

    test_start = perf_counter()

    print("AutoSpot final model evaluation")
    print(f"Device: {device}")
    print(f"Test images: {len(test_dataset)}")
    print(f"Test batches: {len(test_loader)}")

    print(
        "Checkpoint phase: "
        f"{checkpoint['phase']}"
    )

    print(
        "Checkpoint epoch: "
        f"{checkpoint['epoch']}"
    )

    with torch.inference_mode():
        for batch_index, (
            images,
            labels,
        ) in enumerate(
            test_loader,
            start=1,
        ):
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels,
            )

            if not torch.isfinite(loss).item():
                raise RuntimeError(
                    "Test loss is not finite at "
                    f"batch {batch_index}: "
                    f"{loss.item()}"
                )

            batch_sample_count = labels.size(0)

            (
                top_1_correct,
                top_3_correct,
            ) = count_correct_predictions(
                outputs,
                labels,
            )

            total_loss += (
                loss.item()
                * batch_sample_count
            )

            total_samples += batch_sample_count

            total_top_1_correct += (
                top_1_correct
            )

            total_top_3_correct += (
                top_3_correct
            )

            if (
                batch_index % 50 == 0
                or batch_index == len(test_loader)
            ):
                elapsed_seconds = (
                    perf_counter()
                    - test_start
                )

                print(
                    f"Test batch "
                    f"{batch_index}/"
                    f"{len(test_loader)}, "
                    f"elapsed="
                    f"{elapsed_seconds:.1f}s"
                )

    if total_samples == 0:
        raise RuntimeError(
            "No test samples were processed"
        )

    test_loss = (
        total_loss / total_samples
    )

    test_top_1_accuracy = (
        total_top_1_correct
        / total_samples
    )

    test_top_3_accuracy = (
        total_top_3_correct
        / total_samples
    )

    elapsed_seconds = (
        perf_counter()
        - test_start
    )

    results = {
        "architecture": checkpoint["architecture"],
        "checkpoint": str(CHECKPOINT_FILE),
        "checkpoint_phase": checkpoint["phase"],
        "checkpoint_epoch": checkpoint["epoch"],
        "class_count": CLASS_COUNT,
        "test_manifest": str(TEST_MANIFEST),
        "test_images": total_samples,
        "test_batches": len(test_loader),
        "loss": test_loss,
        "top_1_accuracy": test_top_1_accuracy,
        "top_3_accuracy": test_top_3_accuracy,
        "elapsed_seconds": elapsed_seconds,
    }

    save_results(results)

    print()
    print("Final test results")

    print(
        f"  Test loss: "
        f"{test_loss:.4f}"
    )

    print(
        f"  Test top-1: "
        f"{test_top_1_accuracy:.2%}"
    )

    print(
        f"  Test top-3: "
        f"{test_top_3_accuracy:.2%}"
    )

    print(
        f"  Test images: "
        f"{total_samples}"
    )

    print(
        f"  Test time: "
        f"{elapsed_seconds:.1f}s"
    )

    print(
        f"Results saved: "
        f"{RESULTS_FILE}"
    )


if __name__ == "__main__":
    main()
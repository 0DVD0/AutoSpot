from pathlib import Path
from time import perf_counter
import torch 
from torch.utils.data import DataLoader
from app.dataset import CarDataSet
from app.model import create_efficientnet_b0
from app.transform import evaluation_transforms

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path("/Users/dvd/Downloads/image")

VALIDATION_MANIFEST = (AI_SERVICE_ROOT / "data" / "splits" / "validation.csv")

CHECKPOINT_FILE =(AI_SERVICE_ROOT / "models" / "efficientnet_b0_phase3_best.pt")

OUTPUT_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "validation_logits.pt")
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
        IMAGE_ROOT, VALIDATION_MANIFEST, CHECKPOINT_FILE
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

    if CLASS_COUNT <= 0:
        raise ValueError("Class count cant be zero or negative")

    if BATCH_SIZE <= 0:
        raise ValueError("Batch size must be positive")

    if NUM_WORKERS < 0:
        raise ValueError("Workers must be positive")


def load_model(device: torch.device):
    checkpoint = torch.load(CHECKPOINT_FILE, map_location="cpu")

    required_keys = {
        "architecture",
        "phase",
        "epoch",
        "class_count",
        "dry_run",
        "model_state_dict",
    }

    missing_keys = (required_keys - checkpoint.keys())

    if missing_keys:
        raise ValueError(f"Checkpoint is missing keys: {missing_keys}")

    if checkpoint["architecture"] != "efficientnet_b0":
        raise ValueError("Unexpected model")

    if checkpoint["phase"] != 3:
        raise ValueError("Wrong training phase, expected 3")

    if checkpoint["class_count"] != CLASS_COUNT:
        raise ValueError("Class count differs in model")

    if checkpoint["dry_run"]:
        raise ValueError("Checkpoint cant be dry run")

    model = create_efficientnet_b0(CLASS_COUNT, True)

    model.load_state_dict(checkpoint["model_state_dict"])

    model = model.to(device)
    model.eval()

    return model, checkpoint


def main() :
    validate_configuration()
    device = get_device()

    validation_dataset = CarDataSet(VALIDATION_MANIFEST, IMAGE_ROOT, evaluation_transforms)

    validation_loader = DataLoader(dataset= validation_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS, persistent_workers=(NUM_WORKERS > 0))

    model, checkpoint = load_model(device)

    logit_batches = []
    label_batches = []

    image_paths = [
        record["relative_image_path"]
        for record in validation_dataset.reccords
    ]

    export_start = perf_counter()

    print("Logit Export"
          f"Device: {device}"
          f"Validation Images: {len(validation_dataset)}"
          f"Validation Batches: {len(validation_loader)}"
          f"Checkpoint phase: {checkpoint["phase"]}"
          f"Checkpoint epoch: {checkpoint["epoch"]}")

    with torch.inference_mode():
        for batch_index, (images, labels) in enumerate(validation_loader, start=1):

            images = images.to(device)
            logits = model(images)

            if logits.ndim != 2:
                raise RuntimeError("Logits must have two dimensions")
            if logits.shape[1] != CLASS_COUNT:
                raise RuntimeError(f"Unexpected class dimension: {logits.shape[1]}")

            if not torch.isfinite(logits).all().item():
                raise RuntimeError(f"Non_finite logits found: {batch_index}")

            logit_batches.append(logits.detach().cpu())
            label_batches.append(labels.detach().cpu())

            if (batch_index % 50 == 0) or batch_index == len(validation_loader):
                elapsed_seconds = perf_counter() - export_start

                print(f"Batch {batch_index}"
                      f"{len(validation_loader)}"
                      f"Elapsed: {elapsed_seconds:1f}s")

        all_logits = torch.cat(logit_batches, dim=0)
        all_labels = torch.cat(label_batches, dim=0)

        expected_sample_count = len(validation_dataset)

        if all_logits.shape != (expected_sample_count, CLASS_COUNT):
                raise RuntimeError("Unexpected final logits shape:"
                                   f"{tuple(all_logits.shape)}")

        if tuple(all_labels.shape) != (expected_sample_count,):
                raise RuntimeError("Unexpected final label shape:" \
                f"{tuple(all_labels.shape)}")

        if len(image_paths) != expected_sample_count:
                raise RuntimeError("Image path count does not match")
        
        top_predictions = all_logits.topk(k=3, dim=1).indices
        top_1_accuracy = (top_predictions[:,0].eq(all_labels).float().mean().item())
        top_3_accuracy = (top_predictions.eq(all_labels.unsqueeze(1)).any(dim=1).float().mean().item())

        export_data = {
                "architecture": (
                    checkpoint["architecture"]
                ),
                "checkpoint_phase": (
                    checkpoint["phase"]
                ),
                "checkpoint_epoch": (
                    checkpoint["epoch"]
                ),
                "class_count": CLASS_COUNT,
                "manifest_file": str(
                    VALIDATION_MANIFEST
                ),
                "crop_source": (
                    "compcars_ground_truth_boxes"
                ),
                "sample_count": (
                    expected_sample_count
                ),
                "top_1_accuracy": (
                    top_1_accuracy
                ),
                "top_3_accuracy": (
                    top_3_accuracy
                ),
                "logits": all_logits,
                "labels": all_labels,
                "image_paths": image_paths,
            }

        OUTPUT_FILE.parent.mkdir(parents= True, exist_ok=True)

        temp_file = OUTPUT_FILE.with_suffix(".tmp")
        torch.save(export_data, temp_file)
        temp_file.replace(OUTPUT_FILE)

        elapsed_seconds = (
                perf_counter()
                - export_start
            )

        print()
        print("Validation logit export completed")

        print(
                f"Logits shape: "
                f"{tuple(all_logits.shape)}"
            )

        print(
                f"Labels shape: "
                f"{tuple(all_labels.shape)}"
            )

        print(
                f"Validation top-1: "
                f"{top_1_accuracy:.2%}"
            )

        print(
                f"Validation top-3: "
                f"{top_3_accuracy:.2%}"
            )

        print(
                f"Elapsed: "
                f"{elapsed_seconds:.1f}s"
            )

        print(
                f"Saved: {OUTPUT_FILE}"
            )

if __name__ == "__main__":
    main()
from pathlib import Path
import torch
from torch import nn
from torch.utils.data import DataLoader
from app.dataset import CarDataSet
from app.transform import (evaluation_transforms, train_transform)
from app.model import (
    create_efficientnet_b0,
    unfreeze_last_feature_blocks,
)
from time import perf_counter
import json

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

MODEL_DIRECTORY = (
    AI_SERVICE_ROOT / "models"
)

PHASE_2_CHECKPOINT = (
    MODEL_DIRECTORY
    / "efficientnet_b0_phase2_best.pt"
)

CLASS_COUNT = 868

BATCH_SIZE = 32

UNFROZEN_BLOCK_COUNT = 2

BACKBONE_LEARNING_RATE = 0.000005

CLASSIFIER_LEARNING_RATE = 0.00005

WEIGHT_DECAY = 0.0001

EARLY_STOPPING_PATIENCE = 2

DRY_RUN = False

NUM_WORKERS = 2

RANDOM_SEED = 42

EPOCH_COUNT = (
    1 if DRY_RUN else 3
)

MAX_TRAIN_BATCHES = (
    50 if DRY_RUN else None
)

MAX_VALIDATION_BATCHES = (
    20 if DRY_RUN else None
)

def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")

def validate_configuration():
    required_paths = [
        IMAGE_ROOT,
        TRAIN_MANIFEST,
        VALIDATION_MANIFEST,
        PHASE_2_CHECKPOINT
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

    if BACKBONE_LEARNING_RATE <= 0:
        raise ValueError(
            "Backbone learning rate must be positive"
        )

    if CLASSIFIER_LEARNING_RATE <= 0:
        raise ValueError(
            "Classifier learning rate must be positive"
        )

    if UNFROZEN_BLOCK_COUNT <= 0:
        raise ValueError(
            "Unfrozen block count must be positive"
        )

    if NUM_WORKERS < 0:
        raise ValueError(
            "Number of workers cannot be negative"
        )

def create_data_loader():
    train_dataset = CarDataSet(TRAIN_MANIFEST, IMAGE_ROOT, train_transform)

    validation_dataset = CarDataSet(VALIDATION_MANIFEST, IMAGE_ROOT, evaluation_transforms)

    loader_generator = torch.Generator()

    loader_generator.manual_seed(RANDOM_SEED)

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        persistent_workers= (NUM_WORKERS > 0),
        generator=loader_generator
    )

    validation_loader = DataLoader(
        dataset=validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        persistent_workers= (NUM_WORKERS > 0)
    )

    return (train_dataset, validation_dataset, train_loader, validation_loader)

def create_training_components(device: torch.device):
    checkpoint = torch.load(
        PHASE_2_CHECKPOINT,
        map_location="cpu",
    )

    if checkpoint["phase"] != 2:
        raise ValueError(
            "Expected a phase 2 checkpoint"
        )

    if checkpoint["class_count"] != CLASS_COUNT:
        raise ValueError(
            "Checkpoint class count does not match"
        )

    model = create_efficientnet_b0(
        class_count=CLASS_COUNT,
        freeze_backbone=True,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = unfreeze_last_feature_blocks(
        model,
        block_count=UNFROZEN_BLOCK_COUNT,
    )

    backbone_parameters = [
        parameter
        for parameter
        in model.features.parameters()
        if parameter.requires_grad
    ]

    classifier_parameters = [
        parameter
        for parameter
        in model.classifier.parameters()
        if parameter.requires_grad
    ]

    if not backbone_parameters:
        raise RuntimeError(
            "No trainable backbone parameters found"
        )

    if not classifier_parameters:
        raise RuntimeError(
            "No trainable classifier parameters found"
        )

    model = model.to(device)

    criterion = nn.CrossEntropyLoss(
        label_smoothing=0.1
    )

    optimizer = torch.optim.AdamW(
        [
            {
                "params": backbone_parameters,
                "lr": BACKBONE_LEARNING_RATE,
            },
            {
                "params": classifier_parameters,
                "lr": CLASSIFIER_LEARNING_RATE,
            },
        ],
        weight_decay=WEIGHT_DECAY,
    )

    optimizer.load_state_dict(
        checkpoint["optimizer_state_dict"]
    )

    optimizer.param_groups[0]["lr"] = (
        BACKBONE_LEARNING_RATE
    )

    optimizer.param_groups[1]["lr"] = (
        CLASSIFIER_LEARNING_RATE
    )

    return (
        model,
        criterion,
        optimizer,
        checkpoint,
    )

def count_parameters(model):
    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    trainable_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    return(total_parameters, trainable_parameters)

def count_correct_predictions(outputs: torch.Tensor, labels: torch.Tensor):
    top_predictions = outputs.topk(
        k=3,
        dim=1,
    ).indices

    top_1_correct = (
        top_predictions[:, 0]
        .eq(labels)
        .sum()
        .item()
    )

    top_3_correct = (
        top_predictions
        .eq(labels.unsqueeze(1))
        .any(dim=1)
        .sum()
        .item()
    )

    return (
        top_1_correct,
        top_3_correct,
    )

def train_one_epoch(
    model,
    data_loader,
    criterion,
    optimizer,
    device: torch.device,
    max_batches: int | None = None,
):
    model.train()

    frozen_features = (
        model.features[
            :-UNFROZEN_BLOCK_COUNT
        ]
    )

    frozen_features.eval()

    total_loss = 0.0
    total_samples = 0

    total_top_1_correct = 0
    total_top_3_correct = 0

    available_batches = len(data_loader)

    if max_batches is None:
        batch_limit = available_batches
    else:
        batch_limit = min(
            available_batches,
            max_batches,
        )

    if batch_limit <= 0:
        raise ValueError(
            "Training batch limit must be positive"
        )

    epoch_start = perf_counter()

    for batch_index, (
        images,
        labels,
    ) in enumerate(
        data_loader,
        start=1,
    ):
        if batch_index > batch_limit:
            break

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad(
            set_to_none=True
        )

        outputs = model(images)

        loss = criterion(
            outputs,
            labels,
        )

        if not torch.isfinite(loss).item():
            raise RuntimeError(
                f"Loss is not finite at batch "
                f"{batch_index}: {loss.item()}"
            )

        loss.backward()

        optimizer.step()

        batch_sample_count = labels.size(0)

        top_1_correct, top_3_correct = (
            count_correct_predictions(
                outputs.detach(),
                labels,
            )
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
            batch_index % 10 == 0
            or batch_index == batch_limit
        ):
            elapsed_seconds = (
                perf_counter() - epoch_start
            )

            print(
                f"Train batch "
                f"{batch_index}/{batch_limit}, "
                f"loss={loss.item():.4f}, "
                f"elapsed="
                f"{elapsed_seconds:.1f}s"
            )

    if total_samples == 0:
        raise RuntimeError(
            "No training samples were processed"
        )

    average_loss = (
        total_loss / total_samples
    )

    top_1_accuracy = (
        total_top_1_correct
        / total_samples
    )

    top_3_accuracy = (
        total_top_3_correct
        / total_samples
    )

    elapsed_seconds = (
        perf_counter() - epoch_start
    )

    return {
        "loss": average_loss,
        "top_1_accuracy": top_1_accuracy,
        "top_3_accuracy": top_3_accuracy,
        "samples": total_samples,
        "batches": batch_limit,
        "elapsed_seconds": elapsed_seconds,
    }

def validate_one_epoch(
    model,
    data_loader,
    criterion,
    device: torch.device,
    max_batches: int | None = None,
):
    model.eval()

    total_loss = 0.0
    total_samples = 0

    total_top_1_correct = 0
    total_top_3_correct = 0

    available_batches = len(data_loader)

    if max_batches is None:
        batch_limit = available_batches
    else:
        batch_limit = min(
            available_batches,
            max_batches,
        )

    if batch_limit <= 0:
        raise ValueError(
            "Validation batch limit must be positive"
        )

    validation_start = perf_counter()

    with torch.inference_mode():
        for batch_index, (
            images,
            labels,
        ) in enumerate(
            data_loader,
            start=1,
        ):
            if batch_index > batch_limit:
                break

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels,
            )

            if not torch.isfinite(loss).item():
                raise RuntimeError(
                    f"Validation loss is not finite "
                    f"at batch {batch_index}: "
                    f"{loss.item()}"
                )

            batch_sample_count = labels.size(0)

            top_1_correct, top_3_correct = (
                count_correct_predictions(
                    outputs,
                    labels,
                )
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
                batch_index % 10 == 0
                or batch_index == batch_limit
            ):
                elapsed_seconds = (
                    perf_counter()
                    - validation_start
                )

                print(
                    f"Validation batch "
                    f"{batch_index}/"
                    f"{batch_limit}, "
                    f"loss={loss.item():.4f}, "
                    f"elapsed="
                    f"{elapsed_seconds:.1f}s"
                )

    if total_samples == 0:
        raise RuntimeError(
            "No validation samples were processed"
        )

    average_loss = (
        total_loss / total_samples
    )

    top_1_accuracy = (
        total_top_1_correct
        / total_samples
    )

    top_3_accuracy = (
        total_top_3_correct
        / total_samples
    )

    elapsed_seconds = (
        perf_counter()
        - validation_start
    )

    return {
        "loss": average_loss,
        "top_1_accuracy": top_1_accuracy,
        "top_3_accuracy": top_3_accuracy,
        "samples": total_samples,
        "batches": batch_limit,
        "elapsed_seconds": elapsed_seconds,
    }

def save_checkpoint(
    output_file: Path,
    model,
    optimizer,
    epoch: int,
    train_metrics: dict,
    validation_metrics: dict,
):
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_state = {
        name: tensor.detach().cpu()
        for name, tensor
        in model.state_dict().items()
    }

    checkpoint = {
        "architecture": "efficientnet_b0",
        "phase": 3,
        "epoch": epoch,
        "class_count": CLASS_COUNT,
        "dry_run": DRY_RUN,
        "model_state_dict": model_state,
        "optimizer_state_dict": (
            optimizer.state_dict()
        ),
        "train_metrics": train_metrics,
        "validation_metrics": (
            validation_metrics
        ),
        "configuration": {
            "batch_size": BATCH_SIZE,
            "backbone_learning_rate": (
                BACKBONE_LEARNING_RATE
            ),
            "classifier_learning_rate": (
                CLASSIFIER_LEARNING_RATE
            ),
            "unfrozen_block_count": (
                UNFROZEN_BLOCK_COUNT
            ),
            "early_stopping_patience": (
                EARLY_STOPPING_PATIENCE
            ),
            "source_checkpoint": str(
                PHASE_2_CHECKPOINT
            ),
            "weight_decay": WEIGHT_DECAY,
            "random_seed": RANDOM_SEED,
        },
    }

    temporary_file = output_file.with_suffix(
        ".tmp"
    )

    torch.save(
        checkpoint,
        temporary_file,
    )

    temporary_file.replace(output_file)

    print(
        f"Checkpoint saved: {output_file}"
    )

def save_training_history(
    output_file: Path,
    history: list[dict],
):
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = output_file.with_suffix(
        ".tmp"
    )

    temporary_file.write_text(
        json.dumps(
            history,
            indent=2,
        ),
        encoding="utf-8",
    )

    temporary_file.replace(output_file)

    print(
        f"Training history saved: "
        f"{output_file}"
    )

def print_epoch_summary(
    epoch: int,
    train_metrics: dict,
    validation_metrics: dict,
    checkpoint_saved: bool,
):
    print()
    print(f"Epoch {epoch} summary")

    print(
        f"  Train loss: "
        f"{train_metrics['loss']:.4f}"
    )

    print(
        f"  Train top-1: "
        f"{train_metrics['top_1_accuracy']:.2%}"
    )

    print(
        f"  Train top-3: "
        f"{train_metrics['top_3_accuracy']:.2%}"
    )

    print(
        f"  Validation loss: "
        f"{validation_metrics['loss']:.4f}"
    )

    print(
        f"  Validation top-1: "
        f"{validation_metrics['top_1_accuracy']:.2%}"
    )

    print(
        f"  Validation top-3: "
        f"{validation_metrics['top_3_accuracy']:.2%}"
    )

    print(
        f"  Train time: "
        f"{train_metrics['elapsed_seconds']:.1f}s"
    )

    print(
        f"  Validation time: "
        f"{validation_metrics['elapsed_seconds']:.1f}s"
    )

    print(
        f"  Best checkpoint updated: "
        f"{checkpoint_saved}"
    )

def validate_saved_checkpoint(
    checkpoint_file: Path,
):
    if not checkpoint_file.exists():
        raise FileNotFoundError(
            f"Checkpoint was not created: "
            f"{checkpoint_file}"
        )

    if checkpoint_file.stat().st_size == 0:
        raise RuntimeError(
            f"Checkpoint is empty: "
            f"{checkpoint_file}"
        )

    checkpoint = torch.load(
        checkpoint_file,
        map_location="cpu",
    )

    required_keys = {
        "architecture",
        "phase",
        "epoch",
        "class_count",
        "model_state_dict",
        "optimizer_state_dict",
        "train_metrics",
        "validation_metrics",
        "configuration",
    }

    missing_keys = (
        required_keys - checkpoint.keys()
    )

    if missing_keys:
        raise RuntimeError(
            f"Checkpoint is missing keys: "
            f"{sorted(missing_keys)}"
        )

    if checkpoint["class_count"] != CLASS_COUNT:
        raise RuntimeError(
            "Checkpoint class count does not "
            "match the current configuration"
        )

    if checkpoint["phase"] != 3:
        raise RuntimeError(
            "Expected a phase 3 checkpoint"
        )

    print(
        f"Best checkpoint validated: "
        f"epoch {checkpoint['epoch']}"
    )

    return checkpoint



def main():
    validate_configuration()

    torch.manual_seed(RANDOM_SEED)

    device = get_device()

    (
        train_dataset,
        validation_dataset,
        train_loader,
        validation_loader,
    ) = create_data_loader()

    (
        model,
        criterion,
        optimizer,
        phase_2_checkpoint,
    ) = create_training_components(device)

    run_name = (
        "efficientnet_b0_phase3_dry_run"
        if DRY_RUN
        else "efficientnet_b0_phase3"
    )

    checkpoint_file = (
        MODEL_DIRECTORY
        / f"{run_name}_best.pt"
    )

    history_file = (
        MODEL_DIRECTORY
        / f"{run_name}_history.json"
    )

    total_parameters, trainable_parameters = (
        count_parameters(model)
    )

    print("AutoSpot phase 3 max tune")
    print(
    "Loaded phase 2 checkpoint "
    f"from epoch "
    f"{phase_2_checkpoint['epoch']}"
    )

    print(
        "Phase 2 validation top-1: "
        f"{phase_2_checkpoint['validation_metrics']['top_1_accuracy']:.2%}"
    )

    print(
        "Phase 2 validation top-3: "
        f"{phase_2_checkpoint['validation_metrics']['top_3_accuracy']:.2%}"
    )

    print(
        "Backbone learning rate: "
        f"{BACKBONE_LEARNING_RATE}"
    )

    print(
        "Classifier learning rate: "
        f"{CLASSIFIER_LEARNING_RATE}"
    )

    print(
        "Unfrozen feature blocks: "
        f"{UNFROZEN_BLOCK_COUNT}"
    )
    print(f"Device: {device}")
    print(f"Dry run: {DRY_RUN}")
    print(f"Epochs: {EPOCH_COUNT}")
    print(f"Batch size: {BATCH_SIZE}")

    print(
        f"Train images: "
        f"{len(train_dataset)}"
    )

    print(
        f"Validation images: "
        f"{len(validation_dataset)}"
    )

    print(
        f"Train batches available: "
        f"{len(train_loader)}"
    )

    print(
        f"Validation batches available: "
        f"{len(validation_loader)}"
    )

    print(
        f"Maximum train batches: "
        f"{MAX_TRAIN_BATCHES}"
    )

    print(
        f"Maximum validation batches: "
        f"{MAX_VALIDATION_BATCHES}"
    )

    print(
        f"Total parameters: "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters: "
        f"{trainable_parameters:,}"
    )

    history = []

    source_validation_loss = (
    phase_2_checkpoint[
        "validation_metrics"
    ]["loss"]
    )

    best_validation_loss = (
        float("inf")
        if DRY_RUN
        else source_validation_loss
    )

    best_epoch = None

    epochs_without_improvement = 0

    training_start = perf_counter()

    for epoch in range(
        1,
        EPOCH_COUNT + 1,
    ):
        print()
        print(
            f"Starting epoch "
            f"{epoch}/{EPOCH_COUNT}"
        )

        train_metrics = train_one_epoch(
            model=model,
            data_loader=train_loader,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            max_batches=MAX_TRAIN_BATCHES,
        )

        validation_metrics = (
            validate_one_epoch(
                model=model,
                data_loader=validation_loader,
                criterion=criterion,
                device=device,
                max_batches=(
                    MAX_VALIDATION_BATCHES
                ),
            )
        )

        current_validation_loss = (
            validation_metrics["loss"]
        )

        checkpoint_saved = (
            current_validation_loss
            < best_validation_loss
        )

        if checkpoint_saved:
            best_validation_loss = (
                current_validation_loss
            )

            best_epoch = epoch
            epochs_without_improvement = 0

            save_checkpoint(
                output_file=checkpoint_file,
                model=model,
                optimizer=optimizer,
                epoch=epoch,
                train_metrics=train_metrics,
                validation_metrics=(
                    validation_metrics
                ),
            )
        else:
            epochs_without_improvement += 1


        epoch_result = {
            "epoch": epoch,
            "checkpoint_saved": (
                checkpoint_saved
            ),
            "train": train_metrics,
            "validation": (
                validation_metrics
            ),
        }

        history.append(epoch_result)

        save_training_history(
            output_file=history_file,
            history=history,
        )

        print_epoch_summary(
            epoch=epoch,
            train_metrics=train_metrics,
            validation_metrics=(
                validation_metrics
            ),
            checkpoint_saved=(
                checkpoint_saved
            ),
        )

        if (
            not DRY_RUN
            and epochs_without_improvement
            >= EARLY_STOPPING_PATIENCE
        ):
            print(
                "Early stopping activated after "
                f"{epochs_without_improvement} "
                "epochs without validation "
                "improvement"
            )

            break

    total_training_seconds = (
        perf_counter() - training_start
    )

    print()
    print("Phase 3 training completed")

    print(
        f"Total training time: "
        f"{total_training_seconds:.1f}s"
    )

    print(
        f"Best epoch: {best_epoch}"
    )

    print(
        f"Best validation loss: "
        f"{best_validation_loss:.4f}"
    )

    print(
        f"History file: "
        f"{history_file}"
    )

    if best_epoch is None:
        print(
            "Phase 3 did not improve the "
            "phase 2 validation loss."
        )

        print(
            "The phase 2 checkpoint remains "
            "the selected model."
        )

        return

    best_checkpoint = (
        validate_saved_checkpoint(
            checkpoint_file
        )
    )

    print(
        f"Saved checkpoint validation "
        f"top-1: "
        f"{best_checkpoint['validation_metrics']['top_1_accuracy']:.2%}"
    )

    print(
        f"Saved checkpoint validation "
        f"top-3: "
        f"{best_checkpoint['validation_metrics']['top_3_accuracy']:.2%}"
    )
   
if __name__ == "__main__":
    main()
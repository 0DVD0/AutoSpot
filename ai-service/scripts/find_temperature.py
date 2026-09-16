import json
from pathlib import Path

import torch
import torch.nn.functional as F

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "validation_logits.pt")

OUTPUT_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "temperature.json")

def load_validation_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Input file not found")

    export_data = torch.load(INPUT_FILE, map_location="cpu", weights_only=False)

    required_keys = {
        "logits",
        "labels",
        "class_count",
        "sample_count"
    }

    missing_keys = required_keys - export_data.keys()

    if missing_keys:
        raise ValueError(f"Missing keys in validation export: {missing_keys}")

    logits = export_data["logits"].float()
    labels = export_data["labels"].long()

    if logits.ndim != 2:
        raise ValueError("Logits must have two dimensions")
    if labels.ndim != 1:
        raise ValueError("Lables can have only 1 dimension")
    if logits.shape[0] != labels.shape[0]:
        raise ValueError("Logits and labels dont match")

    if not torch.isfinite(logits).all():
        raise ValueError("Logits contain non-finite values")

    return logits, labels, export_data

def calculate_init_loss(logits: torch.Tensor, lables: torch.Tensor, temperature: float):
    scaled_logits = logits / temperature

    return F.cross_entropy(scaled_logits, lables).item()


def find_optimal_temperature(logits: torch.Tensor, labels: torch.Tensor):
    log_temperature = torch.nn.Parameter(torch.zeros(1))

    optimizer = torch.optim.LBFGS([log_temperature], lr=0.1, max_iter=100, line_search_fn="strong_wolfe")

    def closure():
        optimizer.zero_grad()
        temperature = torch.exp(log_temperature)
        loss = F.cross_entropy(logits / temperature, labels)

        loss.backward()

        return loss

    optimizer.step(closure)
    optimal_temperature = (torch.exp(log_temperature).detach().item())

    return optimal_temperature

def calculate_top1_accuracy(logits: torch.Tensor, labels: torch.Tensor, temperature: float):
    predictions = (logits / temperature).argmax(dim=1)

    return predictions.eq(labels).float().mean().item()

def main():
    logits, labels, export_data = load_validation_data()

    init_temperature = 1.0

    loss_before = calculate_init_loss(logits, labels, init_temperature)

    accuracy_before = calculate_top1_accuracy(logits, labels, init_temperature)

    optimal_temperature = find_optimal_temperature(logits, labels)

    loss_after = calculate_init_loss(logits, labels, optimal_temperature)

    accuracy_after = calculate_top1_accuracy(logits, labels, optimal_temperature)

    result = {
        "temperature": optimal_temperature,
        "nll_before": loss_before,
        "nll_after": loss_after,
        "top1_accuracy_before": accuracy_before,
        "top1_accuracy_after": accuracy_after,
        "sample_count": int(labels.shape[0]),
        "class_count": int(logits.shape[1]),
        "checkpoint_phase": export_data[
            "checkpoint_phase"
        ],
        "checkpoint_epoch": export_data[
            "checkpoint_epoch"
        ],
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            result,
            file,
            indent=2,
        )

    print("Temperature scaling completed")
    print(f"Samples: {labels.shape[0]}")
    print(f"Classes: {logits.shape[1]}")
    print(
        f"Optimal temperature: "
        f"{optimal_temperature:.6f}"
    )
    print(f"NLL before: {loss_before:.6f}")
    print(f"NLL after: {loss_after:.6f}")
    print(
        f"Top-1 before: "
        f"{accuracy_before:.2%}"
    )
    print(
        f"Top-1 after: "
        f"{accuracy_after:.2%}"
    )
    print(f"Saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
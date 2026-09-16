import json 
import math
from pathlib import Path
import torch

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]
LOGITS_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "validation_logits.pt")
TEMPERATURE_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "temperature.json")
OUTPUT_FILE = (AI_SERVICE_ROOT / "data" / "calibration" / "confidence_analysis.json")

def load_data():
    if not LOGITS_FILE.exists():
        raise FileNotFoundError(f"Logits file not found: {LOGITS_FILE}")

    if not TEMPERATURE_FILE.exists():
        raise FileNotFoundError(f"Temperature file not found: {TEMPERATURE_FILE}")

    export_data = torch.load(LOGITS_FILE, map_location="cpu", weights_only=False)

    with TEMPERATURE_FILE.open("r", encoding="utf-8") as file:
        temperature_data = json.load(file)

        if "logits" not in export_data:
            raise ValueError("Logits are missing")

        if "labels" not in export_data:
            raise ValueError("Labels are missing")

        if "temperature" not in temperature_data:
            raise ValueError("Temperature is missing")

        logits = export_data["logits"].float()
        labels = export_data["labels"].long()
        temperature = float(temperature_data["temperature"])

        if logits.ndim != 2:
            raise ValueError("Logits must have 2 dimensions")

        if labels.ndim != 1:
            raise ValueError("Labels must have one dimension")

        if logits.shape[0] != labels.shape[0]:
            raise ValueError("Logits and labels have different lenghts")

        if (temperature <= 0 or not math.isfinite(temperature)):
            raise ValueError("Temperature must be finite and positive")

        return logits, labels, temperature

def calculate_calibration_bins(probabilities: torch.Tensor, labels: torch.Tensor, bin_count: int = 10):
        confidences, predictions = (probabilities.max(dim=1))

        correct = predictions.eq(labels)

        bins = []
        ece = 0.0
        sample_count = labels.shape[0]

        for bin_index in range(bin_count):
            lower_bound = bin_index/bin_count
            upper_bound = ((bin_index + 1) / bin_count)
            in_bin = ((confidences > lower_bound) & (confidences <= upper_bound))

            count = int(in_bin.sum().item())

            if count == 0:
                bins.append({
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "count": 0,
                    "coverage": 0.0,
                    "average_confidence": None,
                    "accuracy": None,
                })
                continue
            average_confidence = (confidences[in_bin].mean().item())
            accuracy = (correct[in_bin].float().mean().item())
            coverage = count / sample_count
            ece += coverage * abs(accuracy - average_confidence)
            bins.append(
                {
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "count": count,
                    "coverage": coverage,
                    "average_confidence": (average_confidence),
                    "accuracy": accuracy,
                }
            )
        return ece, bins

def analyze_thresholds(confidences: torch.Tensor, margins: torch.Tensor, correct: torch.Tensor):
    confidence_thresholds =[
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
        0.80,
        0.90
    ] 

    margin_thresholds = [
        0.00,
        0.05,
        0.10,
        0.15,
        0.20,
        0.30,
        0.40,
    ]

    sample_count = confidences.shape[0]
    results = []

    for confidence_threshold in confidence_thresholds:
        for margin_threshold in margin_thresholds:
            accepted = (confidences >= confidence_threshold) & (margins >= margin_threshold)
            accepted_count = int(accepted.sum().item())

            if accepted_count == 0:
                continue

            accepted_accuracy = (correct[accepted].float().mean().item())

            coverage = (accepted_count / sample_count)

            results.append({
                "confidence_threshold": (
                        confidence_threshold
                    ),
                "margin_threshold": (
                        margin_threshold
                    ),
                "accepted_count": (
                        accepted_count
                    ),
                "coverage": coverage,
                "accuracy": (
                        accepted_accuracy
                    ),
            })
    return results


def find_recommended_rule(threshold_results: list[dict], target_accuracy: float):

    eligible_rules = [
        result
        for result in threshold_results
        if result["accuracy"] >= target_accuracy
    ]

    if not eligible_rules:
        return None

    return max(eligible_rules, key=lambda result: (result["coverage"], result["accuracy"]))


def main():
    logits, labels, temperature = load_data()

    uncalibrated_probabilities = (torch.softmax(logits, dim=1))
    calibrated_probabilities = torch.softmax(logits/temperature, dim=1)

    ece_before, bins_before = calculate_calibration_bins(uncalibrated_probabilities, labels)

    ece_after, bins_after = calculate_calibration_bins(calibrated_probabilities, labels)

    top_probabilities, top_indexes = calibrated_probabilities.topk(k=3, dim=1)

    top1_confidences = top_probabilities[:, 0]
    top2_confidences = top_probabilities[:, 1]
    margins = (top1_confidences - top2_confidences)

    top1_predictions = top_indexes[:, 0]

    correct = top1_predictions.eq(labels)

    top1_accuracy = correct.float().mean().item()

    top3_accuracy = top_indexes.eq(labels.unsqueeze(1)).any(dim=1).float().mean().item()

    threshold_results = analyze_thresholds(top1_confidences, margins, correct)

    target_accuracies = [
        0.85,
        0.90,
        0.95
    ]

    recommendations = {}

    for target_accuracy in target_accuracies:
        rule = find_recommended_rule(threshold_results, target_accuracy)

        recommendations[f"{int(target_accuracy * 100)}_percent"] = rule

    result = {
             "temperature": temperature,
            "sample_count": int(labels.shape[0]),
            "class_count": int(logits.shape[1]),
            "top1_accuracy": top1_accuracy,
            "top3_accuracy": top3_accuracy,
            "ece_before": ece_before,
            "ece_after": ece_after,
            "calibration_bins_before": bins_before,
            "calibration_bins_after": bins_after,
            "threshold_results": threshold_results,
            "recommendations": recommendations,
        }
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)

            print("Confidence analysis completed")
    print(f"Temperature: {temperature:.6f}")
    print(f"Samples: {labels.shape[0]}")
    print(f"Top-1 accuracy: {top1_accuracy:.2%}")
    print(f"Top-3 accuracy: {top3_accuracy:.2%}")
    print(f"ECE before: {ece_before:.6f}")
    print(f"ECE after: {ece_after:.6f}")
    print()

    for target_name, rule in (
        recommendations.items()
    ):
        print(f"Target: {target_name}")

        if rule is None:
            print("No matching rule found")
            print()
            continue

        print(
            "Confidence threshold: "
            f"{rule['confidence_threshold']:.0%}"
        )
        print(
            "Margin threshold: "
            f"{rule['margin_threshold']:.0%}"
        )
        print(
            f"Coverage: {rule['coverage']:.2%}"
        )
        print(
            f"Accuracy: {rule['accuracy']:.2%}"
        )
        print(
            f"Accepted: {rule['accepted_count']}"
        )
        print()

    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
import json
import math
from pathlib import Path
from typing import Any
import torch


class ConfidenceCalibrator:
    def __init__(self, temperature_file:Path, confidence_analysis_file: Path):
        temperature_data = self._load_json(temperature_file)
        analysis_data = self._load_json(confidence_analysis_file)

        self.temperature = (self._load_temperature(temperature_data))

        self.high_rule = self._load_rule(analysis_data, "95_percent")
        self.medium_rule = self._load_rule(analysis_data, "90_percent")


    def _load_json(self, file_path: Path) -> dict[str, Any]:
            if not file_path.exists():
                raise FileNotFoundError(f"Calibration file not found: {file_path}")

            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError(f"Calibration file must contain data: {file_path}")

            return data

    def _load_temperature(self, temperature_data: dict[str, Any]):
            if "temperature" not in temperature_data:
                raise ValueError("Temperature not found in data config")

            temperature = float(temperature_data["temperature"])

            if (temperature <= 0 or not math.isfinite(temperature)):
                raise ValueError("Temperature must be positive and finite")

            return temperature

    def _load_rule(self, analysis_data: dict[str, Any], target_name: str):
            recommendations = analysis_data.get("recommendations")

            if not isinstance(recommendations, dict):
                raise ValueError("Confidence is missing")

            rule = recommendations.get(target_name)

            if not isinstance(rule, dict):
                raise ValueError("Confience rule not found")

            required_keys = {
                "confidence_threshold", "margin_threshold"
            }

            missing_keys = (required_keys - rule.keys())

            if missing_keys:
                raise ValueError(f"Rule {target_name} has missing keys:"
                                 f"{sorted(missing_keys)}")

            confidence_threshold = float(rule["confidence_threshold"])

            margin_threshold = float(rule["margin_threshold"])

            if not 0 <= confidence_threshold <= 1:
                raise ValueError(f"Invalid confidence: {target_name}")

            if not 0 <= margin_threshold <= 1:
                raise ValueError(f"Invalid marhgin: {target_name}")

            return {
                "confidence_threshold": confidence_threshold,
                "margin_threshold": margin_threshold
            }

    def _matches_rule(self, confidence: float, margin: float, rule: dict[str, float]):
            return (confidence >= rule["confidence_threshold"] and margin >= rule["margin_threshold"])

    def _get_status(self, confidence: float, margin: float):
            if self._matches_rule(confidence, margin, self.high_rule):
                return "high_confidence"

            if self._matches_rule(confidence, margin, self.medium_rule):
                return "medium_confidence"

            return "uncertain"


    def calibrate_logits(self, logits: torch.Tensor, top_k: int = 3):
            if not isinstance(logits, torch.Tensor):
                raise TypeError("Logits must be Tensor")

            if logits.ndim != 2:
                raise ValueError("Logits must have 2 dimensions")

            if logits.shape[0] != 1:
                raise ValueError("Expected logits with one img")

            class_count = logits.shape[1]

            if class_count < 2:
                raise ValueError("At least 2 classes are required")

            if top_k <= 0:
                raise ValueError("Top-k must be positive")

            if top_k > class_count:
                raise ValueError("Top-k cant be higher that number of classes")

            if not torch.isfinite(logits).all().item():
                raise ValueError("All logits values must be finite")

            with torch.inference_mode():
                calibrated_logits = (logits / self.temperature)

                probabilities = torch.softmax(calibrated_logits, dim=1)

                selected_count = max(top_k, 2)

                top_probabilities, top_indexes = (probabilities.topk(k=selected_count, dim=1))

            confidence= float(top_probabilities[0, 0].item())

            second_confidence = float(top_probabilities[0, 1].item())

            margin = (confidence - second_confidence)

            status = self._get_status(confidence, margin)

            return {
                "status": status,
                "temperature": self.temperature,
                "confidence": confidence,
                "margin": margin,
                "top_probabilities": (
                    top_probabilities[0, :top_k].detach()
                ),
                "top_class_indexes": (
                    top_indexes[0, :top_k].detach()
                ),
            }
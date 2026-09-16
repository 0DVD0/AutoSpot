import json
from pathlib import Path
import torch
from PIL import Image
from app.model import create_efficientnet_b0
from app.transform import evaluation_transforms
from app.calibration import ConfidenceCalibrator

def get_interface_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")

class CarPredictor:
    def __init__(self, checkpoint_file: Path, class_mapping_file: Path, temperature_file: Path, confidence_analysis_file: Path , device: torch.device | None = None):
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Model checkpoint not found {checkpoint_file}")

        if not class_mapping_file.exists():
            raise FileNotFoundError(f"Class mapping not found {class_mapping_file}")

        self.device = (
            device
            if device is not None
            else get_interface_device()
        )

        self.checkpoint = torch.load(
            checkpoint_file, map_location="cpu"
        )

        self.class_mapping = self._load_mapping(class_mapping_file)

        self._validate_checkpoint()

        self.class_count = self.checkpoint[
            "class_count"
        ]

        self._validate_mapping()

        self.calibrator = ConfidenceCalibrator(temperature_file, confidence_analysis_file)

        self.model = create_efficientnet_b0(
            class_count=self.class_count,
            freeze_backbone=True,
        )

        self.model.load_state_dict(
            self.checkpoint["model_state_dict"]
        )

        self.model = self.model.to(self.device)

        self.model.eval()

    def _load_mapping(self, class_mapping_file: Path):
            with class_mapping_file.open(
                "r", encoding="utf-8"
            ) as mapping_stream:
                mapping = json.load(mapping_stream)
            if not isinstance(mapping, dict):
                raise ValueError("Class mapping must be a JSON object")

            if not mapping:
                raise ValueError("Class mapping cannot be empty")

            return mapping

    def _validate_checkpoint(self):
            required_keys = {
                "architecture",
                "phase",
                "epoch",
                "class_count",
                "dry_run",
                "model_state_dict"
            }

            missing_keys = (
                required_keys - self.checkpoint.keys()
            )

            if missing_keys:
                raise ValueError(f"Checkpoint is missing keys: {sorted(missing_keys)}")

            if (self.checkpoint["architecture"] != "efficientnet_b0"):
                raise ValueError("Unexpected model architecture")

            if self.checkpoint["phase"] != 3:
                raise ValueError("Expected a phase 3 checkpoint")

            if self.checkpoint["class_count"] <= 0:
                raise ValueError("Class count must be positive")

            if self.checkpoint["dry_run"]:
                raise ValueError("Dry Run checkpoint cannot be used")

    def _validate_mapping(self):
            expected_keys = {
                str(class_index)
                for class_index in range(self.class_count)
            }

            actual_keys = set(self.class_mapping.keys())

            if actual_keys != expected_keys:
                missing_keys = (expected_keys - actual_keys)

                extra_keys = (actual_keys - expected_keys)

                raise ValueError("Class mapping does not match"
                                 f"Missing: {missing_keys}"
                                 f"Extra: {extra_keys}")

            for class_key, class_details in (self.class_mapping.items()):
                required_details = {
                    "brand_id",
                    "model_id",
                    "brand",
                    "model"
                }

                missing_details = (required_details - class_details.keys())

                if missing_details:
                    raise ValueError(f"Class {class_key} is missing details: {sorted(missing_details)}")


    def predict_image(self, image: Image.Image, top_k: int = 3):
            if not isinstance(image, Image.Image):
                raise TypeError("Image must be PIL image")

            image = image.convert("RGB")

            image_tensor = evaluation_transforms(image)

            return self.predict_tensor(image_tensor, top_k)

    def predict_tensor(self, image_tensor: torch.Tensor, top_k: int = 3):
            if top_k <= 0:
                raise ValueError("Top-K must be positive")

            if top_k > self.class_count:
                raise ValueError("Top-k cannot be higher than class count")

            if image_tensor.ndim == 3:
                image_tensor = (image_tensor.unsqueeze(0))
            
            if image_tensor.ndim != 4:
                raise ValueError("Expected a 3 or 4 dimension tensor")

            if image_tensor.shape[0] != 1:
                raise ValueError("Expected one image at a time")

            
            image_tensor = image_tensor.to(self.device)

            with torch.inference_mode():
                logits = self.model(image_tensor)

                calibrated_result = (self.calibrator.calibrate_logits(logits, top_k))
                predictions = self._decode_predictions(calibrated_result["top_probabilities"], calibrated_result["top_class_indexes"])


            return {
                 "status": calibrated_result["status"],
                "temperature": (
                    calibrated_result["temperature"]
                ),
                "confidence": (
                    calibrated_result["confidence"]
                ),
                "margin": calibrated_result["margin"],
                "predictions": predictions,
            }

    def _decode_predictions(self, probabilities: torch.Tensor, class_indexes: torch.Tensor):
            predictions = []

            for rank, (probability, class_index) in enumerate(zip(probabilities, class_indexes),start=1):
                class_index_value = int(
                    class_index.item()
                )

                class_details = (
                    self.class_mapping[
                        str(class_index_value)
                    ]
                )

                predictions.append(
                    {
                        "rank": rank,
                        "class_index": (
                            class_index_value
                        ),
                        "brand_id": (
                            class_details[
                                "brand_id"
                            ]
                        ),
                        "model_id": (
                            class_details[
                                "model_id"
                            ]
                        ),
                        "brand": (
                            class_details["brand"]
                        ),
                        "model": (
                            class_details["model"]
                        ),
                        "score": float(
                            probability.item()
                        ),
                    }
                )

            return predictions

    def get_class_details(self, class_index: int):
            class_key = str(class_index)

            if class_key not in self.class_mapping:
                raise KeyError(
                    f"Unknown class index: "
                    f"{class_index}"
                )

            return self.class_mapping[
                class_key
            ]
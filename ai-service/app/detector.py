import torch
from PIL import Image
from torchvision.models.detection import (
    FasterRCNN_MobileNet_V3_Large_FPN_Weights,
    fasterrcnn_mobilenet_v3_large_fpn,
)

def select_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")

class CarDetector:
    def __init__(self, device: torch.device | None = None , minimum_score: float = 0.5, crop_padding_ratio: float = 0.08):

        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("Minimum score has to be between 0 aa 1")

        self.minimum_score = minimum_score

        if crop_padding_ratio < 0:
            raise ValueError(
                "Crop padding ratio cannot be negative"
            )

        self.crop_padding_ratio = (
            crop_padding_ratio
        )

        self.vehicle_categories = {
            "car", "truck"
        }

        self.device = (
            device if device is not None
            else select_device()
        )

        self.weights = FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT

        self.preprocess = self.weights.transforms()

        self.model = fasterrcnn_mobilenet_v3_large_fpn(weights=self.weights)

        self.model = self.model.to(self.device)

        self.model.eval()

        self.categories = (self.weights.meta["categories"])



    def _run_model(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise TypeError("Image must be PIL image")
            
        image = image.convert("RGB")

        image_tensor = self.preprocess(image)

        image_tensor = image_tensor.to(self.device)

        with torch.inference_mode():
            outputs = self.model([image_tensor])

        raw_output = outputs[0]

        cpu_output = {}

        for output_name, output_tensor in raw_output.items():
            cpu_output[output_name] = output_tensor.detach().cpu()

        return cpu_output

    def detect_image(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise ValueError("Image must be PIL")

        image = image.convert("RGB")

        raw_output = self._run_model(image)
        boxes, labels, scores = raw_output["boxes"], raw_output["labels"], raw_output["scores"]

        vehicle_detections = []

        for box, label, score in zip(boxes, labels, scores):
            label_index = int(label.item())
            label_name = self.categories[label_index]
            score_value = float(score.item())

            if label_name not in self.vehicle_categories:
                continue

            if score_value < self.minimum_score: 
                continue

            (
                left_value,
                top_value,
                right_value,
                bottom_value,
            ) = box.tolist()

            left = max(
                0,
                int(left_value),
            )

            top = max(
                0,
                int(top_value),
            )

            right = min(
                image.width,
                int(right_value),
            )

            bottom = min(
                image.height,
                int(bottom_value),
            )

            if right <= left:
                continue
            if bottom <= top:
                continue

            detection_width = right - left
            detection_height = bottom - top

            detection_area = (
                detection_width
                * detection_height
            )

            image_area = (
                image.width
                * image.height
            )

            area_ratio = (
                detection_area
                / image_area
            )

            vehicle_detections.append(
                {
                    "label": label_name,
                    "label_index": label_index,
                    "score": score_value,
                    "box": {
                        "left": left,
                        "top": top,
                        "right": right,
                        "bottom": bottom,
                    },
                    "width": detection_width,
                    "height": detection_height,
                    "area": detection_area,
                    "area_ratio": area_ratio,
                }
            )

        vehicle_detections.sort(
            key=lambda detection:(detection["area"]),
            reverse=True
        )

        return vehicle_detections

    def select_primary_detection(self, detections: list[dict]):
        if not detections:
            return None

        return detections[0]

    def crop_detection(self, image: Image.Image, detection: dict):

        if not isinstance(image, Image.Image):
            raise ValueError("Expected PIL image")

        if "box" not in detection:
            raise ValueError("Detection does not contain a bounding box")

        image = image.convert("RGB")

        box = detection["box"]

        left = box["left"]
        top = box["top"]
        right = box["right"]
        bottom = box["bottom"]

        box_width = right - left

        box_height = bottom - top

        if box_width <= 0 or box_height <= 0:
            raise ValueError(
                "Detection box is invalid"
            )

        horizontal_padding = int(box_width * self.crop_padding_ratio)
        vertical_padding = int(box_height * self.crop_padding_ratio)

        padded_left = max(0, left - horizontal_padding)

        padded_top = max(0, top - vertical_padding)

        padded_right = min(image.width, right + horizontal_padding)

        padded_bottom = min(image.height, bottom + vertical_padding)

        padded_box = {
            "left": padded_left,
            "top": padded_top,
            "right": padded_right,
            "bottom": padded_bottom
        }

        cropped_image = image.crop(
            (padded_left, padded_top, padded_right, padded_bottom)
        )

        return cropped_image, padded_box
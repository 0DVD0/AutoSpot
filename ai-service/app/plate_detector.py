import cv2
import numpy as np
from PIL import Image, ImageOps
from open_image_models import create_detector

class PlateDetector:
    def __init__(self, minimum_score: float = 0.25, model_name: str = "yolo-v9-s-608-license-plate-end2end"):
        if not 0.0 <= minimum_score <= 1.0:
            raise ValueError("Minimum score must be between 0 and 1")

        self.minimum_score = minimum_score

        self.detector = create_detector(model_name, conf_thresh=minimum_score)

    def detect_plates(self, image: Image.Image) -> list[dict]:
        if not isinstance(image,Image.Image):
            raise TypeError("Image must be a PIL image")

        source_image = ImageOps.exif_transpose(image).convert("RGB")

        rgb_frame = np.asarray(source_image)

        bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        raw_detections = self.detector.predict(bgr_frame)

        plate_detections = []

        for detection in raw_detections:
            box = detection.bounding_box.clamp(source_image.width, source_image.height)

            if box.is_empty:
                continue

            plate_detections.append(
               { 
                   "score": float(detection.confidence),
                    "box": {
                        "left": box.x1,
                        "top": box.y1,
                        "right": box.x2,
                        "bottom": box.y2
                    }
                }
            )

        return plate_detections
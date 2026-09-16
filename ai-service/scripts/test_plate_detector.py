import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from app.plate_detector import PlateDetector


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python scripts/test_plate_detector.py IMAGE_PATH"
    )

image_path = Path(sys.argv[1]).resolve()

source_image = ImageOps.exif_transpose(
    Image.open(image_path)
).convert("RGB")

detector = PlateDetector()

detections = detector.detect_plates(
    source_image
)

preview = cv2.cvtColor(
    np.asarray(source_image),
    cv2.COLOR_RGB2BGR,
)

for detection in detections:
    box = detection["box"]

    cv2.rectangle(
        preview,
        (box["left"], box["top"]),
        (box["right"], box["bottom"]),
        (0, 0, 255),
        3,
    )

    print(
        "Plate:",
        box,
        "confidence:",
        detection["score"],
    )

output_directory = (
    PROJECT_ROOT / "data" / "previews"
)

output_directory.mkdir(
    parents=True,
    exist_ok=True,
)

output_path = (
    output_directory
    / f"{image_path.stem}_plates.jpg"
)

cv2.imwrite(
    str(output_path),
    preview,
)

print("Detected plates:", len(detections))
print("Preview saved to:", output_path)
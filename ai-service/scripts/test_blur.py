import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from app.plate_detector import PlateDetector
from app.privacy_processor import PrivacyProcessor


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python scripts/test_plate_blur.py IMAGE_PATH"
    )

image_path = Path(sys.argv[1]).resolve()

if not image_path.is_file():
    raise SystemExit(
        f"Image was not found: {image_path}"
    )

plate_detector = PlateDetector()

privacy_processor = PrivacyProcessor(
    plate_detector=plate_detector
)

with Image.open(image_path) as image:
    processed_image, detections = (
        privacy_processor.blur_plates(image)
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
    / f"{image_path.stem}_blurred.jpg"
)

processed_image.save(
    output_path,
    format="JPEG",
    quality=95,
)

print("Blurred plates:", len(detections))
print("Processed image saved to:", output_path)
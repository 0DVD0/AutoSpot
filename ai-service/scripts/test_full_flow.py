import sys
from pathlib import Path
from io import BytesIO
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(PROJECT_ROOT),
)

from app.image_encoder import ImageEncoder
from app.detector import CarDetector
from app.identification_service import CarIdentificationService, NoVehicleDetectedError
from app.plate_detector import PlateDetector
from app.post_image_service import PostImageService
from app.privacy_processor import PrivacyProcessor
from app.vlm_predictor import VlmPredictor


if len(sys.argv) != 2:
    raise SystemExit(
        "Usage: python scripts/test_post_image_flow.py IMAGE_PATH"
    )

image_path = Path(sys.argv[1]).resolve()

if not image_path.is_file():
    raise SystemExit(
        f"Image not found: {image_path}"
    )


def main():
    car_detector = CarDetector()
    plate_detector = PlateDetector()
    vlm_predictor = VlmPredictor()

    identification_service = (
        CarIdentificationService(
            detector=car_detector,
            vlm_predictor=vlm_predictor,
        )
    )

    privacy_processor = PrivacyProcessor(plate_detector=plate_detector)

    image_encoder = ImageEncoder()

    post_image_service = PostImageService(
        identification_service=identification_service,
        privacy_processor=privacy_processor,
        image_encoder=image_encoder

    )

    try:
        with Image.open(image_path) as image:
            result = post_image_service.process(
                image
            )

        print("Identification:")
        print(
            result.identification.model_dump_json(
                indent=2
            )
        )

        print(
            "Detected plates:",
            len(result.plate_detections),
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
            / f"{image_path.stem}_processed.jpg"
        )


        output_path.write_bytes(result.processed_image)

        with Image.open(BytesIO(result.processed_image)) as verification_image:
            exif_count = len(verification_image.getexif())

        print("Output size:", len(result.processed_image), "bytes")

        print(
            "Processed image:",
            output_path,
        )

        print("EXIF:", exif_count)

    except NoVehicleDetectedError:
        print(
            "No vehicle was detected in the image"
        )

    finally:
        post_image_service.close()


if __name__ == "__main__":
    main()
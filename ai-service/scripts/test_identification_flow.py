from pathlib import Path
from PIL import Image
from app.detector import CarDetector
from app.identification_service import CarIdentificationService, NoVehicleDetectedError
from app.predictor import CarPredictor
from app.vlm_predictor import VlmPredictor
from app.privacy_processor import PrivacyProcessor
from app.plate_detector import PlateDetector

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_PATH = Path(
    "/Users/dvd/Desktop/TEST_IMAGES/images-2.jpeg"
)



def main():
    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(f"No image found for: {IMAGE_PATH}")

    print("Loading car detector")
    detector = CarDetector()


    print("Connecting to Qwen VLM")
    vlm_predictor = VlmPredictor()

    identification_service = CarIdentificationService(detector=detector, vlm_predictor=vlm_predictor)

    try:
        with Image.open(IMAGE_PATH) as source_image:
            image = source_image.convert("RGB")

        print("Running indetification flow")

        result = identification_service.identify(image)
        print(" "
              "Identification result:")
        print(result.model_dump_json(indent=2))
    except NoVehicleDetectedError as error:
        print("No vehicle found")
    finally:
        identification_service.close()

if __name__ == "__main__":
    main()
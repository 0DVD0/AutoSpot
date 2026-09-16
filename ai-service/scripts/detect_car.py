from pathlib import Path

from PIL import Image

from app.detector import CarDetector
from app.predictor import CarPredictor


IMAGE_PATH = Path(
    "/Users/dvd/Downloads/supra_old.jpeg"
)

AI_SERVICE_ROOT = (
    Path(__file__).resolve().parents[1]
)

CHECKPOINT_FILE = (
    AI_SERVICE_ROOT
    / "models"
    / "efficientnet_b0_phase3_best.pt"
)

CLASS_MAPPING_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "class_mapping.json"
)

CROP_OUTPUT_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "previews"
    / "detected_vehicle_crop.jpg"
)

TEMPERATURE_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "calibration"
    / "temperature.json"
)

CONFIDENCE_ANALYSIS_FILE = (
    AI_SERVICE_ROOT
    / "data"
    / "calibration"
    / "confidence_analysis.json"
)

MAX_RESULTS_TO_PRINT = 10


def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Image is missing: "
            f"{IMAGE_PATH}"
        )

    with Image.open(
        IMAGE_PATH
    ) as source_image:
        image = source_image.convert(
            "RGB"
        )

    detector = CarDetector()

    detections = detector.detect_image(
        image
    )

    print("AutoSpot vehicle detection test")
    print(f"Device: {detector.device}")
    print(f"Image: {IMAGE_PATH}")

    print(
        f"Image size: "
        f"{image.width}×{image.height}"
    )

    print(
        f"Vehicle detections: "
        f"{len(detections)}"
    )

    for detection_index, detection in enumerate(
        detections,
        start=1,
    ):
        print()

        print(
            f"Detection {detection_index}"
        )

        print(
            f"  Label: "
            f"{detection['label']}"
        )

        print(
            f"  Score: "
            f"{detection['score']:.2%}"
        )

        print(
            f"  Box: "
            f"{detection['box']}"
        )

        print(
            f"  Size: "
            f"{detection['width']}×"
            f"{detection['height']}"
        )

        print(
            f"  Area ratio: "
            f"{detection['area_ratio']:.2%}"
        )

    if not detections:
            raise RuntimeError(
                "No vehicle was detected"
            )

    primary_detection = (
            detector.select_primary_detection(
                detections
            )
        )

    if primary_detection is None:
            raise RuntimeError(
                "A primary vehicle could "
                "not be selected"
            )

    (
            cropped_vehicle,
            padded_box,
        ) = detector.crop_detection(
            image=image,
            detection=primary_detection,
        )

    CROP_OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    cropped_vehicle.save(
            CROP_OUTPUT_FILE,
            quality=95,
        )

    predictor = CarPredictor(
            checkpoint_file=CHECKPOINT_FILE,
            class_mapping_file=(
                CLASS_MAPPING_FILE
            ),
            temperature_file=TEMPERATURE_FILE,
            confidence_analysis_file=CONFIDENCE_ANALYSIS_FILE
        )

    result = predictor.predict_image(cropped_vehicle, top_k=3)

    predictions = result["predictions"]
    print()
    print("Primary vehicle")

    print(
            f"  Detection score: "
            f"{primary_detection['score']:.2%}"
        )

    print(
        f"  Original box: "
            f"{primary_detection['box']}"
        )

    print(
            f"  Padded box: "
            f"{padded_box}"
        )

    print(
            f"  Crop size: "
            f"{cropped_vehicle.width}×"
            f"{cropped_vehicle.height}"
        )

    print(
            f"  Crop saved: "
            f"{CROP_OUTPUT_FILE}"
        )

    print()

    print(f"Status: {result['status']}")
    print(
        f"Confidence: "
        f"{result['confidence']:.2%}"
    )
    print(
        f"Margin: "
        f"{result['margin']:.2%}"
    )
    print()
    print("Car model predictions")

    for prediction in predictions:
            print(
                f"  {prediction['rank']}. "
                f"{prediction['brand']} "
                f"{prediction['model']} "
                f"— {prediction['score']:.2%}"
            )

    if detections[0]["label"] not in {
        "car",
        "truck",
    }:
        raise RuntimeError(
            "Unexpected detection category"
        )

    print()
    print("Clean vehicle detection test passed")

if __name__ == "__main__":
    main()
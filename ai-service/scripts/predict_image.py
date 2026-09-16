from pathlib import Path
from PIL import Image
from app.dataset import CarDataSet
from app.predictor import CarPredictor
from app.transform import evaluation_transforms


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

IMAGE_ROOT = Path(
    "/Users/dvd/Downloads/image"
)

VALIDATION_MANIFEST = (
    AI_SERVICE_ROOT
    / "data"
    / "splits"
    / "validation.csv"
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

IMAGE_INDEX = 0
TOP_K = 3


def main():
    validation_dataset = CarDataSet(
        manifest_file=VALIDATION_MANIFEST,
        image_root=IMAGE_ROOT,
        transform=evaluation_transforms,
    )

    image_record = (
        validation_dataset.reccords[
            IMAGE_INDEX
        ]
    )

    expected_class_index = int(
        image_record["class_index"]
    )

    image_path = (
        IMAGE_ROOT
        / image_record["relative_image_path"]
    )

    with Image.open(image_path) as source_image:
        car_image = source_image.convert(
            "RGB"
        )

    crop_box = (
        validation_dataset.build_crop_box(
            record=image_record,
            image_width=car_image.width,
            image_height=car_image.height,
        )
    )

    cropped_car_image = (
        car_image.crop(crop_box)
    )

    predictor = CarPredictor(
        checkpoint_file=CHECKPOINT_FILE,
        class_mapping_file=(
            CLASS_MAPPING_FILE
        ),
        temperature_file=TEMPERATURE_FILE,
        confidence_analysis_file=CONFIDENCE_ANALYSIS_FILE
    )

    expected_details = (
        predictor.get_class_details(
            expected_class_index
        )
    )

    result = predictor.predict_image(cropped_car_image, TOP_K)

    predictions = result["predictions"]

    print("AutoSpot single-image prediction")
    print(f"Device: {predictor.device}")

    print(
        "Image: "
        f"{image_record['relative_image_path']}"
    )

    print(
        "Expected: "
        f"{expected_details['brand']} "
        f"{expected_details['model']} "
        f"(class {expected_class_index})"
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
    print("Predictions")

    for prediction in predictions:
        print(
            f"  {prediction['rank']}. "
            f"{prediction['brand']} "
            f"{prediction['model']} "
            f"— {prediction['score']:.2%} "
            f"(class "
            f"{prediction['class_index']})"
        )

    predicted_class_indexes = {
        prediction["class_index"]
        for prediction in predictions
    }

    expected_is_in_top_k = (
        expected_class_index
        in predicted_class_indexes
    )

    print()

    print(
        f"Expected class is in top "
        f"{TOP_K}: "
        f"{expected_is_in_top_k}"
    )

    if len(predictions) != TOP_K:
        raise RuntimeError(
            "Predictor returned an unexpected "
            "number of predictions"
        )

    scores = [
        prediction["score"]
        for prediction in predictions
    ]

    if scores != sorted(
        scores,
        reverse=True,
    ):
        raise RuntimeError(
            "Predictions are not ordered "
            "by descending score"
        )

    print("Single-image prediction test passed")


if __name__ == "__main__":
    main()
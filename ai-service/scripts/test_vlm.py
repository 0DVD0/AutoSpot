from pathlib import Path
from time import perf_counter
from PIL import Image
from app.vlm_predictor import VlmPredictor

IMAGE_PATH = Path("/Users/dvd/Downloads/mclaren.jpg")

def main():
    if not IMAGE_PATH.is_file():
        raise FileNotFoundError(f"Image not found in downloads")

    predictor = VlmPredictor(allow_thinking_json=True)

    try:
        with Image.open(IMAGE_PATH) as image:
            started_at = perf_counter()
            prediction = predictor.predict_image(image)
            elapsed_seconds = perf_counter() - started_at

        print(prediction.model_dump_json(indent=2))
        print(f"Duration: {elapsed_seconds:.2f} seconds")
    finally:
        predictor.close()

if __name__ == "__main__":
    main()
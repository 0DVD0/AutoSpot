from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.detector import CarDetector
from app.identification_service import CarIdentificationService
from app.image_encoder import ImageEncoder
from app.plate_detector import PlateDetector
from app.post_image_service import PostImageService
from app.privacy_processor import PrivacyProcessor
from app.vlm_predictor import VlmPredictor
from app.backend_ai_service.routers import image_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    car_detector = CarDetector()
    plate_detector = PlateDetector()
    vlm_predictor = VlmPredictor()

    identification_service = CarIdentificationService(car_detector, vlm_predictor)

    privacy_proccessor = PrivacyProcessor(plate_detector)

    image_encoder = ImageEncoder()

    app.state.post_image_service = (
        PostImageService(identification_service=identification_service, privacy_processor=privacy_proccessor, image_encoder=image_encoder)
    )

    yield

    app.state.post_image_service.close()

app = FastAPI(title="AutoSpot AI Service", lifespan=lifespan)

app.include_router(image_router.router)

@app.get("/health")
def health():
    return {"status": "ok"}
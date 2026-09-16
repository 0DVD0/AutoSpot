from time import perf_counter
import logging
from PIL import Image, ImageOps
from app.detector import CarDetector
from app.identification_schema import IdentificationResult

from app.predictor import CarPredictor
from app.vlm_predictor import VlmPredictor

logger = logging.getLogger(__name__)

class NoVehicleDetectedError(RuntimeError):
    pass


class CarIdentificationService:
    def __init__(self, detector: CarDetector, vlm_predictor: VlmPredictor):
        self.detector = detector
        self.vlm_predictor = vlm_predictor
       

    def close(self):
            self.vlm_predictor.close()

    
    def identify(self, image: Image.Image) -> IdentificationResult:
        if not isinstance(image, Image.Image):
            raise TypeError("Image must be a PIL Image")

        source_image = ImageOps.exif_transpose(image).convert("RGB")

        detector_started = perf_counter()

        detections = self.detector.detect_image(source_image)

        detector_duration = (
            perf_counter() - detector_started
        ) * 1000

        primary_detection = (
            self.detector.select_primary_detection(detections)
        )

        if primary_detection is None:
            raise NoVehicleDetectedError(
                "No vehicle was detected in the image"
            )

        cropped_vehicle, padded_box = self.detector.crop_detection(
            source_image,
            primary_detection,
        )

        vlm_started = perf_counter()

        try:
            vlm_prediction = self.vlm_predictor.predict_image(
                cropped_vehicle
            )
        except RuntimeError:
            logger.exception("VLM prediction failed")

            vlm_duration = (
                perf_counter() - vlm_started
            ) * 1000

            return IdentificationResult(status="unavailable", brand=None, model=None, detection_score=primary_detection["score"], detection_box=padded_box, vlm_available=False, predictor_model=(self.vlm_predictor.model_name), detector_duration_ms=detector_duration, vlm_duration_ms=vlm_duration)

        vlm_duration = (perf_counter() - vlm_started) * 1000

        if (vlm_prediction.model is not None and vlm_prediction.brand is not None):
            result_status = "suggested"
        elif vlm_prediction.brand is not None:
            result_status = "brand_only"
        else: 
            result_status = "not_identified"


        return IdentificationResult(
            status=result_status,
            brand=vlm_prediction.brand,
            model= vlm_prediction.model,
            detection_score=primary_detection["score"],
            detection_box=padded_box,
            vlm_available=True,
            predictor_model=self.vlm_predictor.model_name,
            detector_duration_ms=detector_duration,
            vlm_duration_ms=vlm_duration,
        )
            
        

         
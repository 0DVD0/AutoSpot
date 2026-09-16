from PIL import Image, ImageOps
from dataclasses import dataclass

from app.identification_schema import IdentificationResult
from app.identification_service import CarIdentificationService
from app.privacy_processor import PrivacyProcessor
from app.image_encoder import ImageEncoder


@dataclass 
class PostImageProcessingResult:
    identification: IdentificationResult
    processed_image: bytes
    content_type: str
    plate_detections: list[dict]

@dataclass 
class CleanImageResult:
    image_bytes: bytes
    content_type:str
    plate_detections: list[dict]

class PostImageService:
    def __init__(self, identification_service: CarIdentificationService, privacy_processor: PrivacyProcessor, image_encoder: ImageEncoder):
        self.identification_service = identification_service
        self.privacy_processor = privacy_processor
        self.image_encoder = image_encoder

    def close(self):
        self.identification_service.close()

    def identify(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise TypeError("Image is not PIL format")

        source_image = ImageOps.exif_transpose(image).convert("RGB")

        return self.identification_service.identify(source_image)

    def clean(self, image: Image.Image):
        if isinstance(image, Image.Image):
            raise TypeError("Image is not PIL format")

        source_image = ImageOps.exif_transpose(image).convert("RGB")

        processed_image, plate_detections = self.privacy_processor.blur_plates(source_image)

        encoded_image = self.image_encoder.encode_jpeg(image)

        return CleanImageResult(encoded_image.content, encoded_image.content_type, plate_detections)
    
    def process(self, image: Image.Image):
        identification = self.identify(image)
        clean = self.clean(image)
        
        
        return PostImageProcessingResult(
            identification=identification, processed_image=clean.content, content_type=clean.content_type, plate_detections=clean.plate_detection
        ) 
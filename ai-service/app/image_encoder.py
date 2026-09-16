from dataclasses import dataclass
from io import BytesIO
from PIL import ImageOps, Image

@dataclass (frozen=True)
class EncodedImage:
    content: bytes
    content_type: str
    extension: str

class ImageEncoder:
    def __init__(self, maximum_dimension: int = 2048, maximum_size_bytes: int = 5 * 1024 * 1024):

        if maximum_dimension <= 0:
            raise ValueError("Dimension must be a positive number")

        if maximum_size_bytes <= 0:
            raise ValueError("Size must be a pozitive number")

        self.maximum_dimension = maximum_dimension
        self.maximum_size_bytes = maximum_size_bytes

    def encode_jpeg(self, image: Image.Image) -> EncodedImage:
        if not isinstance(image, Image.Image):
            raise TypeError("Image must be PIL")

        prepared_image = ImageOps.exif_transpose(image).convert("RGB")

        prepared_image.thumbnail((self.maximum_dimension, self.maximum_dimension), Image.Resampling.LANCZOS)

        clean_image = Image.new("RGB", prepared_image.size)

        clean_image.paste(prepared_image)

        for quality in (90, 85, 80, 75, 70):
            with BytesIO() as buffer:
                clean_image.save(buffer, format="JPEG", quality=quality, optimize= True)

                images_bytes = buffer.getvalue()

            if len(images_bytes) <= self.maximum_size_bytes:
                return EncodedImage(content=images_bytes, content_type="image/jpeg", extension=".jpg")

        raise ValueError("Processed image is still too large")
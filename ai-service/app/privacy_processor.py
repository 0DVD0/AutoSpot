from PIL import ImageOps, ImageFilter, Image, ImageDraw
from app.plate_detector import PlateDetector

class PrivacyProcessor:
    def __init__(self, plate_detector: PlateDetector, minimum_blur_radius: int = 10):
        
        if minimum_blur_radius <= 0:
            raise ValueError("Blur radius has to be positive") 

        self.plate_detector = plate_detector
        self.blur_radius = minimum_blur_radius

    
    def blur_plates(self, image: Image.Image):
        if not isinstance(image, Image.Image):
            raise TypeError("Image must be PIL")

        source_image = ImageOps.exif_transpose(image).convert("RGB")

        processed_image = source_image.copy()

        detections = self.plate_detector.detect_plates(source_image)

        for detection in detections:
            box = detection["box"]
            left = box["left"]
            top = box["top"]
            right = box["right"]
            bottom = box["bottom"]

            if right <= left or bottom <= top:
                continue

            feather_radius = 4

            blend_left = max(
                0,
                left - feather_radius * 2,
            )

            blend_top = max(
                0,
                top - feather_radius * 2,
            )

            blend_right = min(
                source_image.width,
                right + feather_radius * 2,
            )

            blend_bottom = min(
                source_image.height,
                bottom + feather_radius * 2,
            )

            blend_box = (
                blend_left,
                blend_top,
                blend_right,
                blend_bottom,
            )

            plate_region = processed_image.crop(
                blend_box
            )

            region_height = bottom - top

            blur_radius = max(
                self.blur_radius,
                int(region_height * 0.55),
            )

            blurred_region = plate_region.filter(
                ImageFilter.GaussianBlur(
                    radius=blur_radius
                )
            )

            mask = Image.new(
                "L",
                plate_region.size,
                0,
            )

            mask_draw = ImageDraw.Draw(mask)

            mask_draw.rectangle(
                (
                    left - blend_left,
                    top - blend_top,
                    right - blend_left,
                    bottom - blend_top,
                ),
                fill=255,
            )

            smooth_mask = mask.filter(
                ImageFilter.GaussianBlur(
                    radius=feather_radius
                )
            )

            processed_image.paste(
                blurred_region,
                blend_box,
                smooth_mask,
            )

        return processed_image, detections
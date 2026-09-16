import csv
from pathlib import Path
from typing import Callable
from PIL import Image
from torch.utils.data import Dataset

class CarDataSet(Dataset):
    def __init__(self, manifest_file: Path, image_root: Path, transform: Callable | None = None, crop_padding_ratio: float = 0.08):
        if not manifest_file.exists():
            raise FileNotFoundError(f"Manifest file not found {manifest_file}")

        if not image_root.exists():
            raise FileNotFoundError(f"Image file not found {image_root}")

        if crop_padding_ratio < 0:
            raise ValueError("Crop padding ration cannot be negative")

        self.image_root = image_root
        self.transform = transform
        self.crop_padding = crop_padding_ratio

        with manifest_file.open(
            "r", encoding="utf-8", newline=""
        ) as manifest:
            reader = csv.DictReader(manifest)
            self.reccords = list(reader)

        if not self.reccords:
            raise ValueError(f"Manifest is empty: {manifest_file}")

    def __len__(self):
        return len(self.reccords)

    def build_crop_box(self, record: dict, image_width: int, image_height: int):
        x_min = int(record["x_min"])
        x_max = int(record["x_max"])
        y_min = int(record["y_min"])
        y_max = int(record["y_max"])

        bounding_width = x_max - x_min
        bounding_height = y_max - y_min

        horizontal_padding = int(bounding_width * self.crop_padding)
        vertical_padding = int(bounding_height * self.crop_padding)

        left = max(0, x_min - horizontal_padding)
        top = max(0, y_min - vertical_padding)

        right = min(image_width, x_max + horizontal_padding)

        bottom = min(image_height, y_max + vertical_padding)

        if right <= left or bottom <= top:
            raise ValueError("Crop box invalid")

        return left, top, right, bottom

    def __getitem__(self, index: int):
        record = self.reccords[index]

        image_path = self.image_root / record["relative_image_path"]

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with Image.open(image_path) as source_img:
            image = source_img.convert("RGB")

            crop_box = self.build_crop_box(record, image.width, image.height)

            image = image.crop(crop_box)

            if self.transform is not None:
                image = self.transform(image)

            label = int(record["class_index"])

            return image, label
from torchvision import transforms
from torchvision.transforms import InterpolationMode

IMAGE_SIZE = 224

IMAGENET_MEAN = (
    0.485,
    0.456,
    0.406
)

IMAGENET_STANDART_DEVIATION = (
    0.229,
    0.224,
    0.225
)

train_transform = transforms.Compose(
    [
    transforms.Resize(
        (IMAGE_SIZE, IMAGE_SIZE), interpolation=InterpolationMode.BICUBIC
    ),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=5),
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.10, hue=0.02),
    transforms.ToTensor(),
    transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STANDART_DEVIATION)
]
)

evaluation_transforms = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STANDART_DEVIATION)
    ]
)
import csv
import random
from collections import Counter
from pathlib import Path

DATASET_ROOT = Path("/Users/dvd/Downloads")
IMAGE_ROOT = DATASET_ROOT / "image"
LABEL_ROOT = DATASET_ROOT / "label"

AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

SELECTED_CLASSES_FILE = (
    AI_SERVICE_ROOT / "data" / "selected_classes.csv"
)

SPLITS_DIRECTORY = (
    AI_SERVICE_ROOT / "data" / "splits"
)

TRAIN_FILE = SPLITS_DIRECTORY / "train.csv"
VALIDATION_FILE = SPLITS_DIRECTORY / "validation.csv"
TEST_FILE = SPLITS_DIRECTORY / "test.csv"

RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
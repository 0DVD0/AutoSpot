from app.detector import CarDetector


def main():
    detector = CarDetector()

    print("AutoSpot detector loading test")
    print(f"Device: {detector.device}")

    print(
        "Detector type: "
        f"{type(detector.model).__name__}"
    )

    print(
        "Category count: "
        f"{len(detector.categories)}"
    )

    print(
        "Contains car category: "
        f"{'car' in detector.categories}"
    )

    print(
        "Contains truck category: "
        f"{'truck' in detector.categories}"
    )

    if detector.model.training:
        raise RuntimeError(
            "Detector is still in "
            "training mode"
        )

    if "car" not in detector.categories:
        raise RuntimeError(
            "Detector does not contain "
            "the car category"
        )

    if "truck" not in detector.categories:
        raise RuntimeError(
            "Detector does not contain "
            "the truck category"
        )

    print("Detector loading test passed")


if __name__ == "__main__":
    main()
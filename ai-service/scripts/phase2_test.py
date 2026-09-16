from pathlib import Path

import torch

from app.model import (
    create_efficientnet_b0,
    unfreeze_last_feature_blocks,
)


AI_SERVICE_ROOT = Path(__file__).resolve().parents[1]

PHASE_1_CHECKPOINT = (
    AI_SERVICE_ROOT
    / "models"
    / "efficientnet_b0_phase1_best.pt"
)

CLASS_COUNT = 868
UNFROZEN_BLOCK_COUNT = 2

BACKBONE_LEARNING_RATE = 0.00001
CLASSIFIER_LEARNING_RATE = 0.0001
WEIGHT_DECAY = 0.0001

def count_parameters(parameters):
    return sum(
        parameter.numel()
        for parameter in parameters
    )

def main():
    if not PHASE_1_CHECKPOINT.exists():
        raise FileNotFoundError(
            f"Phase 1 checkpoint is missing: "
            f"{PHASE_1_CHECKPOINT}"
        )

    checkpoint = torch.load(
        PHASE_1_CHECKPOINT,
        map_location="cpu",
    )

    if checkpoint["phase"] != 1:
        raise ValueError(
            "Expected a phase 1 checkpoint"
        )

    if checkpoint["class_count"] != CLASS_COUNT:
        raise ValueError(
            "Checkpoint class count does not match"
        )

    model = create_efficientnet_b0(
        class_count=CLASS_COUNT,
        freeze_backbone=True,
    )


    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model = unfreeze_last_feature_blocks(
        model,
        block_count=UNFROZEN_BLOCK_COUNT,
    )

    backbone_parameters = [
    parameter
    for parameter in model.features.parameters()
    if parameter.requires_grad
    ]

    classifier_parameters = [
        parameter
        for parameter in model.classifier.parameters()
        if parameter.requires_grad
    ]

    backbone_parameter_ids = {
    id(parameter)
    for parameter in backbone_parameters
    }

    classifier_parameter_ids = {
        id(parameter)
        for parameter in classifier_parameters
    }

    if not backbone_parameter_ids.isdisjoint(
        classifier_parameter_ids
    ):
        raise RuntimeError(
            "Optimizer parameter groups overlap"
        )

    optimizer = torch.optim.AdamW(
        [
            {
                "params": backbone_parameters,
                "lr": BACKBONE_LEARNING_RATE,
            },
            {
                "params": classifier_parameters,
                "lr": CLASSIFIER_LEARNING_RATE,
            },
        ],
        weight_decay=WEIGHT_DECAY,
    )

    optimizer_backbone_parameter_count = (
        count_parameters(
            optimizer.param_groups[0]["params"]
        )
    )

    optimizer_classifier_parameter_count = (
        count_parameters(
            optimizer.param_groups[1]["params"]
        )
    )

    if optimizer_backbone_parameter_count != 1_129_392:
        raise RuntimeError(
            "Unexpected backbone optimizer "
            f"parameter count: "
            f"{optimizer_backbone_parameter_count:,}"
        )

    if optimizer_classifier_parameter_count != 1_111_908:
        raise RuntimeError(
            "Unexpected classifier optimizer "
            f"parameter count: "
            f"{optimizer_classifier_parameter_count:,}"
        )

    if (
        optimizer.param_groups[0]["lr"]
        != BACKBONE_LEARNING_RATE
    ):
        raise RuntimeError(
            "Incorrect backbone learning rate"
        )

    if (
        optimizer.param_groups[1]["lr"]
        != CLASSIFIER_LEARNING_RATE
    ):
        raise RuntimeError(
            "Incorrect classifier learning rate"
        )

    print(
    "Backbone optimizer group: "
    f"{optimizer_backbone_parameter_count:,} "
    "parameters, "
    f"learning rate="
    f"{optimizer.param_groups[0]['lr']}"
    )

    print(
        "Classifier optimizer group: "
        f"{optimizer_classifier_parameter_count:,} "
        "parameters, "
        f"learning rate="
        f"{optimizer.param_groups[1]['lr']}"
    )

    total_parameters = count_parameters(
        model.parameters()
    )

    trainable_parameters = count_parameters(
        parameter
        for parameter in model.parameters()
        if parameter.requires_grad
    )

    trainable_feature_parameters = (
        count_parameters(
            parameter
            for parameter
            in model.features.parameters()
            if parameter.requires_grad
        )
    )

    trainable_classifier_parameters = (
        count_parameters(
            parameter
            for parameter
            in model.classifier.parameters()
            if parameter.requires_grad
        )
    )

    print(
        f"Loaded phase 1 epoch: "
        f"{checkpoint['epoch']}"
    )

    print(
        f"Total parameters: "
        f"{total_parameters:,}"
    )

    print(
        f"Trainable parameters: "
        f"{trainable_parameters:,}"
    )

    print(
        f"Trainable feature parameters: "
        f"{trainable_feature_parameters:,}"
    )

    print(
        f"Trainable classifier parameters: "
        f"{trainable_classifier_parameters:,}"
    )

    for block_index, block in enumerate(
        model.features
    ):
        block_is_trainable = any(
            parameter.requires_grad
            for parameter in block.parameters()
        )

        print(
            f"Feature block {block_index}: "
            f"trainable={block_is_trainable}"
        )
    if trainable_parameters != 2_241_300:
            raise RuntimeError(
                f"Unexpected trainable parameter "
                f"count: {trainable_parameters:,}"
            )

    for block in model.features[:-2]:
        if any(
            parameter.requires_grad
            for parameter in block.parameters()
        ):
            raise RuntimeError(
                "A frozen feature block is trainable"
            )

    for block in model.features[-2:]:
        if not all(
            parameter.requires_grad
            for parameter in block.parameters()
        ):
            raise RuntimeError(
                "An unfrozen feature block contains "
                "frozen parameters"
            )

    print("Phase 2 model test passed")


if __name__ == "__main__":
    main()
    
from torch import nn
from torchvision.models import (EfficientNet_B0_Weights, efficientnet_b0)

def create_efficientnet_b0(class_count: int, freeze_backbone: bool = True):
    if class_count <= 0:
        raise ValueError("Class count must be higher than 0")

    weights = EfficientNet_B0_Weights.DEFAULT

    model = efficientnet_b0(weights=weights)

    if freeze_backbone:
        for parameter in model.features.parameters():
            parameter.requires_grad = False

    input_feature_count = (model.classifier[1].in_features)

    model.classifier[1] = nn.Linear(in_features=input_feature_count, out_features=class_count)

    return model

def unfreeze_last_feature_blocks(
    model,
    block_count: int = 2,
):
    feature_block_count = len(
        model.features
    )

    if block_count <= 0:
        raise ValueError(
            "Block count must be positive"
        )

    if block_count > feature_block_count:
        raise ValueError(
            f"Cannot unfreeze {block_count} "
            f"blocks because the model has only "
            f"{feature_block_count} feature blocks"
        )

    for parameter in model.features.parameters():
        parameter.requires_grad = False

    blocks_to_unfreeze = (
        model.features[-block_count:]
    )

    for block in blocks_to_unfreeze:
        for parameter in block.parameters():
            parameter.requires_grad = True

    for parameter in model.classifier.parameters():
        parameter.requires_grad = True

    return model


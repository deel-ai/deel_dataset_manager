# -*- encoding: utf-8 -*-

from torchvision.datasets import ImageFolder

from . import BlinkDataset


def load(version: str = "latest", force_update: bool = False) -> ImageFolder:
    """ Load the blink dataset and returns a corresponding torch wrapper.

    Args:
        version: Version of the dataset.
        settings: The settings to use for this dataset, or `None` to use the
        default settings.

    Returns:
        A `ImageFolder` object for the blink dataset.
    """
    return ImageFolder(BlinkDataset(version).load(force_update))

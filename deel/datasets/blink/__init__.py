# -*- encoding: utf-8 -*-

import numpy as np
import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class BlinkDataset(Dataset):

    """ Class for the blink dataset. """

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("blink", version, settings)

    def load(self, force_update: bool = False) -> pathlib.Path:
        return super().load(force_update=force_update).joinpath("final_db_anonymous")


def load(
    framework: typing.Optional[str] = None,
    version: str = "latest",
    force_update: bool = False,
    image_shape: typing.Tuple[int, int, int] = (64, 64, 3),
) -> typing.Any:
    """ Load the blink dataset in the queried format.

    Args:
        framework: Framework to use ("pytorch" or "tensorflow").
        version: Version of the dataset.
        force_update: Force update of the local dataset if possible.
        image_shape: Shape of the image (3-tuple) in the dataset.

    Returns:
        The blink dataset in the format specified by `framework`.

    Raises:
        ValueError: If the `framework` is invalid.
    """

    # Pytorch:
    if framework in ["pytorch", "torch"]:
        from .pytorch import load as load_pytorch

        return load_pytorch(version=version, force_update=force_update)
    # Tensorflow:
    elif framework == "tensorflow":
        from .tensorflow import load as load_tensorflow

        return load_tensorflow(
            version=version, force_update=force_update, image_shape=image_shape
        )

    else:
        raise ValueError(
            "Framework '{}' not implemented for blink dataset.".format(framework)
        )

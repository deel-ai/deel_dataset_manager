# -*- encoding: utf-8 -*-

import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class BlinkDataset(Dataset):

    """ Class for the blink dataset. """

    _default_mode: str = "tensorflow"

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

    def load_pytorch(self, path: pathlib.Path):
        """ Load method for `pytorch` mode. """
        from torchvision.datasets import ImageFolder

        return ImageFolder(self.load_path(path))

    def load_tensorflow(
        self,
        path: pathlib.Path,
        percent_train: int = 40,
        percent_val: int = 40,
        random_seed: int = 0,
        image_shape: typing.Tuple[int, int, int] = (64, 64, 3),
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 100]).
            percent_val: Percentage of validation data ([0, 100]).
            random_seed: Random seed to use to dispatch data.
            image_shape: Shape of the generated image.

        Returns:
            A tuple `(train, valildation, xtest, ytest, label_names)` where
            `train` and `validation` are `tensorflow.data.Dataset`s corresponding
            to training and validation data, `xtest` are the inputs for
            test dataset (list of `Path`), `ytest` the labels, and `label_names`
            the label names.
        """
        from .tensorflow import TensorflowData

        return TensorflowData(self.load_path(path), random_seed).prepare(
            percent_train, percent_val, image_shape
        )

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("final_db_anonymous")

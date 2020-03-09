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
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.

        Returns:
            A tuple `(train, valildation, test)` where `train`, `validation`
            and `test` are `tensorflow.data.Dataset`s corresponding
            to training, validation data and test data.
        """
        from ..utils import load_tensorflow_image_dataset

        return load_tensorflow_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
        )

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("final_db_anonymous")

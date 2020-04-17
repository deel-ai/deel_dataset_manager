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

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("final_db_anonymous")

    def load_pytorch(
        self,
        path: pathlib.Path,
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        include_warnings: bool = False,
        include_flips: bool = False,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
        transform: typing.Callable = None,
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            include_warnings: Include the warning class in the datasets.
            include_flips: Include flipped images in the datasets.
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.
            transform: Transformation to apply on dataset.

        Returns:
            A two-tuple whose first element is a tuple `(train, valildation, test)`
            where `train`, `validation` and `test` are `torch.utils.data.Dataset`s
            corresponding to training, validation data and test data, and whose
            second element is a dictionary containing dataset extra information.
        """
        from ..utils import load_pytorch_image_dataset

        if not include_warnings:
            # Aggregate rotation classes:
            def aggregate_fn(x: str) -> typing.Optional[str]:
                if x == "warnings":
                    return None
                return x

        else:
            # Default aggregate function:
            def aggregate_fn(x: str) -> typing.Optional[str]:
                return x

        if not include_flips:

            def filter_fn(x: str, y: pathlib.Path) -> bool:
                return x.find("_flip") == -1

        else:

            def filter_fn(x: str, y: pathlib.Path) -> bool:
                return True

        datasets, idx_to_class = load_pytorch_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
            aggregate_fn=aggregate_fn,
            filter_fn=filter_fn,
            transform=transform,
        )

        return datasets, self._make_class_info(idx_to_class)

    def load_tensorflow(
        self,
        path: pathlib.Path,
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        include_warnings: bool = False,
        include_flips: bool = False,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            include_warnings: Include the warning class in the datasets.
            include_flips: Include flipped images in the datasets.
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.

        Returns:
            A two-tuple whose first element is a tuple `(train, valildation, test)`
            where `train`, `validation` and `test` are `tensorflow.data.Dataset`s
            corresponding to training, validation data and test data, and whose
            second element is a dictionary containing dataset extra information.
        """
        from ..utils import load_tensorflow_image_dataset

        if not include_warnings:
            # Aggregate rotation classes:
            def aggregate_fn(x: str) -> typing.Optional[str]:
                if x == "warnings":
                    return None
                return x

        else:
            # Default aggregate function:
            def aggregate_fn(x: str) -> typing.Optional[str]:
                return x

        if not include_flips:

            def filter_fn(x: str, y: pathlib.Path) -> bool:
                return x.find("_flip") == -1

        else:

            def filter_fn(x: str, y: pathlib.Path) -> bool:
                return True

        datasets, idx_to_class = load_tensorflow_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
            aggregate_fn=aggregate_fn,
            filter_fn=filter_fn,
        )

        return datasets, self._make_class_info(idx_to_class)

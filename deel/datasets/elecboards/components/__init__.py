# -*- encoding: utf-8 -*-

import pathlib
import typing

from ...dataset import Dataset
from ...settings import Settings


class ElecboardsComponentsDataset(Dataset):

    # Default mode for the dataset (basic):
    _default_mode = "numpy"

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("elecboards-components", version, settings)

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        return path.joinpath("components")

    def _aggregate_rotation_fn(self, x: str):
        split = x.split("_")
        if split[-1].startswith("Rot"):
            split = split[:-1]
        return "_".join(split)

    def load_numpy(
        self,
        path: pathlib.Path,
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
        aggregate_rotation: bool = False,
    ):
        """ Load method for the `numpy` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.
            aggregate_rotation: If True, rotations for a single components will
            aggregated into a single class, if False, no aggregation is made and
            each rotation of each component will be a different class.

        Returns:
            A two-tuple whose first element is a tuple `(train, valildation, test)`
            where `train`, `validation` and `test` are `numpy.ndarray`s corresponding
            to training, validation data and test data, and whose second element is a
            dictionary containing dataset extra information.
        """

        from ...utils import load_numpy_image_dataset

        if aggregate_rotation:
            # Aggregate rotation classes:
            aggregate_fn = self._aggregate_rotation_fn
        else:
            # Default aggregate function:
            def aggregate_fn(x: str) -> str:
                return x

        datasets, idx_to_class = load_numpy_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
            aggregate_fn=aggregate_fn,
        )

        return datasets, self._make_class_info(idx_to_class)

    def load_pytorch(
        self,
        path: pathlib.Path,
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
        aggregate_rotation: bool = False,
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.
            aggregate_rotation: If True, rotations for a single components will
            aggregated into a single class, if False, no aggregation is made and
            each rotation of each component will be a different class.

        Returns:
            A two-tuple whose first element is a tuple `(train, valildation, test)`
            where `train`, `validation` and `test` are `torch.utils.data.Dataset`s
            corresponding to training, validation data and test data, and whose
            second element is a dictionary containing dataset extra information.
        """
        from ...utils import load_pytorch_image_dataset

        if aggregate_rotation:
            # Aggregate rotation classes:
            aggregate_fn = self._aggregate_rotation_fn
        else:
            # Default aggregate function:
            def aggregate_fn(x: str) -> str:
                return x

        datasets, idx_to_class = load_pytorch_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
            aggregate_fn=aggregate_fn,
        )

        return datasets, self._make_class_info(idx_to_class)

    def load_tensorflow(
        self,
        path: pathlib.Path,
        percent_train: float = 0.4,
        percent_val: float = 0.4,
        shuffle: typing.Union[int, bool] = True,
        image_size: typing.Tuple[int, int] = (64, 64),
        aggregate_rotation: bool = False,
    ):
        """ Load method for the `tensorflow` mode.

        Args:
            percent_train: Percentage of training data ([0, 1]).
            percent_val: Percentage of validation data ([0, 1]).
            shuffle: True to shuffle, or the random seed to use to shuffle data,
            or False to not shuffle at all.
            image_size: Size of the generated image.
            aggregate_rotation: If True, rotations for a single components will
            aggregated into a single class, if False, no aggregation is made and
            each rotation of each component will be a different class.

        Returns:
            A two-tuple whose first element is a tuple `(train, valildation, test)`
            where `train`, `validation` and `test` are `tensorflow.data.Dataset`s
            corresponding to training, validation data and test data, and whose
            second element is a dictionary containing dataset extra information.
        """
        from ...utils import load_tensorflow_image_dataset

        if aggregate_rotation:
            # Aggregate rotation classes:
            aggregate_fn = self._aggregate_rotation_fn
        else:
            # Default aggregate function:
            def aggregate_fn(x: str) -> str:
                return x

        datasets, idx_to_class = load_tensorflow_image_dataset(
            self.load_path(path),
            image_size=image_size,
            train_split=(percent_train, percent_val),
            shuffle=shuffle,
            aggregate_fn=aggregate_fn,
        )

        return datasets, self._make_class_info(idx_to_class)

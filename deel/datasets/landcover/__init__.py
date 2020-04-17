# -*- encoding: utf-8 -*-

import h5py
import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class LandcoverDataset(Dataset):

    # Default (and only) mode:
    _default_mode: str = "numpy"

    # Dataset consists of a single ".h5" file:
    _single_file: bool = True

    # Available keys:
    h5_keys: typing.List[str] = ["patches", "labels"]

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        super().__init__("landcover", version, settings)

    def load_numpy(self, path: pathlib.Path):
        # Basic load of patches / labels:
        hdf5 = h5py.File(path, "r")
        data = tuple(hdf5[k][:] for k in self.h5_keys)
        hdf5.close()
        return data

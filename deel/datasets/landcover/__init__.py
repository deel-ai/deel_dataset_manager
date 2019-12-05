# -*- encoding: utf-8 -*-

import h5py
import pathlib
import typing

from ..dataset import Dataset
from ..settings import Settings


class LandCoverDataset(Dataset):

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

    def load(self, force_update: bool = False) -> pathlib.Path:
        # We return the first (only) .h5 file in the directory:
        return next(super().load(force_update).glob("*.h5"))


class LandCoverResolutionDataset(LandCoverDataset):

    h5_keys: typing.List[str] = ["patches", "labels", "sensibilities"]

    def __init__(
        self, version: str = "latest", settings: typing.Optional[Settings] = None
    ):
        """
        Args:
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        Dataset.__init__(self, "landcover-resolution", version, settings)


def load(
    bias: str = "distribution",
    framework: typing.Optional[str] = None,
    version: str = "latest",
    force_update: bool = False,
) -> typing.Union[typing.Tuple]:
    """ Load one of the landcover dataset.

    Args:
        bias: Type of dataset to load. Either "distribution" or "resolution".
        framework: Framework to use or `None` to returns raw data.
        version: Version of the dataset.
        Currently has no effect.
        force_update: Force update of the local dataset if possible.

    Returns:
        The landcover dataset in the format specified by `framework`.

    Raises:
        ValueError: If either the `bias` or the `framework` is invalid.
    """

    # Load the dataset
    if bias == "distribution":
        dataset = LandCoverDataset(version)
    elif bias == "resolution":
        dataset = LandCoverResolutionDataset(version)
    else:
        raise ValueError("Unknown bias '{}' for landcover dataset.".format(bias))

    h5path = dataset.load(force_update=force_update)

    # No framework, load the dataset from the HDF5 file as numpy arrays
    if framework is None:
        hdf5 = h5py.File(h5path, "r")
        data = tuple(hdf5[k][:] for k in dataset.h5_keys)
        hdf5.close()
        return data

    else:
        raise ValueError(
            "Framework '{}' not implemented for landcover dataset.".format(framework)
        )

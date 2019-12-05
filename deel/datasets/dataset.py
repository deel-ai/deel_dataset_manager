# -*- encoding: utf-8 -*-

import abc
import pathlib
import typing

from .settings import Settings, get_default_settings


class Dataset(abc.ABC):

    """
    Dataset is the base class for all DEEL dataset. A `Dataset` object
    is an abstract class that can be used to easily interface with the local
    file system to access datasets files using the `load` method.
    """

    # Name and version of the dataset:
    _name: str
    _version: str

    # The settings to use:
    _settings: Settings

    def __init__(
        self,
        name: str,
        version: str = "latest",
        settings: typing.Optional[Settings] = None,
    ):
        """ Creates a new dataset of the given name and version.

        Args:
            name: Name of the dataset.
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        self._name = name
        self._version = version

        if settings is None:
            self._settings = get_default_settings()
        else:
            self._settings = settings

    def load(self, force_update: bool = False) -> pathlib.Path:
        """ Load this dataset and the return the location of the
        dataset.

        Args:
            force_update: Force update of the dataset if possible.

        Returns:
            A path to the location of the local dataset.
        """
        return self._settings.make_provider().get_folder(
            self._name, self._version, force_update=force_update
        )

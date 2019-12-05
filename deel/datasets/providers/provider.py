# -*- encoding: utf-8 -*-

import abc
import pathlib
import typing


class DatasetNotFoundError(Exception):

    """ Exception thrown by providers when the requested dataset
    is not found. """

    def __init__(self, name: str, version: typing.Optional[str] = None):
        """
        Args:
            name: Name of the dataset not found.
            version: Version of the dataset not found.
        """
        super().__init__("Dataset {} not found.".format(name))


class Provider(abc.ABC):

    """ The `Provider` class is an abstract interface for classes
    that provides access to dataset storages. """

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:
        """ Retrieve the root folder for the given dataset.

        Args:
            name: Name of the dataset to retrieve the folder for.
            version: Version of the dataset to retrieve the folder for.
            force_update: Force the update of the local dataset if possible.
            May have no effect on some providers.

        Returns:
            A path to the root folder for the given dataset name.

        Raises:
            DatasetNotFoundError: If the requested dataset was not found by this
            provider.
        """
        pass

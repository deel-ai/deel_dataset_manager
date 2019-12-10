# -*- encoding: utf-8 -*-

import os
import pathlib

from .provider import DatasetNotFoundError, Provider


class LocalProvider(Provider):

    """ A `LocalProvider` is a provider that look-up datasets in
    a local location (a folder). """

    # The root folder where datasets should be looked-up:
    _root_folder: pathlib.Path

    def __init__(self, root_folder: os.PathLike):
        """
        Args:
            root_folder: Root folder to look-up datasets.
        """
        self._root_folder = pathlib.Path(root_folder)

    def _make_folder(self, name: str, version: str = "latest") -> pathlib.Path:
        """ Create the path for the corresponding dataset, without checking
        if it exists or not.

        Args:
            name: Name of the dataset to retrieve the folder for.
            version: Version of the dataset to retrieve the folder for.

        Returns:
            A path to the root folder for the given dataset name.
        """
        return self._root_folder.joinpath(name, version)

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:

        # Retrieve the path of the dataset:
        path = self._make_folder(name, version)

        if not path.exists():
            raise DatasetNotFoundError(name, version)

        return path

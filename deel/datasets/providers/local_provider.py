# -*- encoding: utf-8 -*-

import os
import pathlib
import typing

from .exceptions import (
    DatasetNotFoundError,
    VersionNotFoundError,
    DatasetVersionNotFoundError,
)
from .provider import Provider


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

    def _make_folder(
        self, name: str, version: typing.Optional[str] = None
    ) -> pathlib.Path:
        """ Create the path for the corresponding dataset, without checking
        if it exists or not.

        Args:
            name: Name of the dataset to retrieve the folder for.
            version: Version of the dataset, or `None` to retrieve the root folder.

        Returns:
            If `version` is `None`, a path to the root folder for the given dataset,
            otherwize, a path to the folder containing the specified version for the
            given dataset.
        """
        folder = self._root_folder.joinpath(name)
        if version is not None:
            folder = folder.joinpath(version)
        return folder

    def _list_version(self, path: pathlib.Path) -> typing.List[str]:
        """ List the available versions for the dataset under the
        given path.

        Args:
            path: Path to a dataset folder.

        Returns:
            A list of versions for the given folder.
        """
        return [c.name for c in path.iterdir()]

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:

        # Retrieve the path of the dataset:
        path = self._make_folder(name)

        if not path.exists():
            raise DatasetNotFoundError(name)

        # Find the matching version:
        try:
            version = self.get_version(version, self._list_version(path))
        except VersionNotFoundError:
            raise DatasetVersionNotFoundError(name, version)

        return path.joinpath(version)

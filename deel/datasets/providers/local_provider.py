# -*- encoding: utf-8 -*-

import os
import pathlib
import shutil
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

    @property
    def root_folder(self) -> pathlib.Path:
        """ Returns: The local path to root folder for the datasets. """
        return self._root_folder

    def _remove_hidden_values(self, values: typing.List[str]) -> typing.List[str]:
        """ Filter the given list by removing hidden values (folders, files). A value
        is considered hidden if:
          - it starts with a dot;
          - it is exactly "lost+found".

        Args:
            values: The list of values to filter.

        Returns:
            The filtered list of values.
        """

        def accept(value):

            if value.startswith("."):
                return False

            if value == "lost+found":
                return False

            return True

        return [value for value in values if accept(value)]

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
        return self._remove_hidden_values([c.name for c in path.iterdir()])

    def list_datasets(self) -> typing.List[str]:
        return self._remove_hidden_values([c.name for c in self._root_folder.iterdir()])

    def list_versions(self, dataset: str) -> typing.List[str]:
        path = self._make_folder(dataset)
        if not path.exists():
            raise DatasetNotFoundError(dataset)
        return self._list_version(path)

    def del_folder(self, name: str, version: str, keep_dataset: bool = False):
        """ Delete the folder corresponding to the given dataset version.
        If after deleting this dataset, there are no versions remaining,
        the dataset folder is also removed, unless `keep_dataset` is `True`.

        Args:
            name: Name of the dataset to delete.
            version: Version of the dataset to delete.
            keep_dataset: `True` to not remove the dataset folder
            when there are no remaining versions.
        """
        path = self._make_folder(name, version)
        shutil.rmtree(path)

        if not keep_dataset and not self.list_versions(name):
            self._make_folder(name).rmdir()

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

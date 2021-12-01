# -*- coding: utf-8 -*-
# Copyright IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL is a research program operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import pathlib
import shutil
import typing

from .exceptions import DatasetNotFoundError
from .exceptions import DatasetVersionNotFoundError
from .exceptions import VersionNotFoundError
from .provider import Provider


class LocalProvider(Provider):

    """
    A `LocalProvider` is a provider that look-up datasets in
    a local location (a folder).
    """

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
        """
        Returns:
            The local path to root folder for the datasets.
        """
        return self._root_folder

    def _remove_hidden_values(self, values: typing.List[str]) -> typing.List[str]:
        """
        Filter the given list by removing hidden values (folders, files). A value
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
        """
        Create the path for the corresponding dataset, without checking
        if it exists or not.

        Args:
            name: Name of the dataset to retrieve the folder for.
            version: Version of the dataset, or `None` to retrieve the root folder.

        Returns:
            If `version` is `None`, a path to the root folder for the given dataset,
            otherwise, a path to the folder containing the specified version for the
            given dataset.
        """
        folder = self._root_folder.joinpath(name)
        if version is not None:
            folder = folder.joinpath(version)
        return folder

    def _list_versions(self, path: pathlib.Path) -> typing.List[str]:
        """
        List the available versions for the dataset under the
        given path.

        Args:
            path: Path to a dataset folder.

        Returns:
            A list of versions for the given folder.
        """
        return self._remove_hidden_values([c.name for c in path.iterdir()])

    def list_datasets(self) -> typing.List[str]:
        if not self._root_folder.exists():
            return []
        return self._remove_hidden_values([c.name for c in self._root_folder.iterdir()])

    def list_versions(self, dataset: str) -> typing.List[str]:
        path = self._make_folder(dataset)
        if not path.exists():
            raise DatasetNotFoundError(dataset)
        return self._list_versions(path)

    def del_folder(self, name: str, version: str, keep_dataset: bool = False):
        """
        Delete the folder corresponding to the given dataset version.
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
        self,
        name: str,
        version: str = "latest",
        force_update: bool = False,
        returns_version: bool = False,
    ) -> typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, str]]:

        # Retrieve the path of the dataset:
        path = self._make_folder(name)

        if not path.exists():
            raise DatasetNotFoundError(name)

        # Find the matching version:
        try:
            version = self.get_version(version, self._list_versions(path))
        except VersionNotFoundError:
            raise DatasetVersionNotFoundError(name, version)

        path = path.joinpath(version)

        if returns_version:
            return path, version
        else:
            return path

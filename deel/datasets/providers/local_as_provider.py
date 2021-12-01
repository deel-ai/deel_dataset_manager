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

from tqdm import tqdm

from .exceptions import DatasetNotFoundError
from .remote_provider import RemoteFile, RemoteProvider

# from .remote_provider import RemoteFile andRemoteProvider


class LocalFile(RemoteFile):

    """
    Representing a local file as local provider file.
    """

    # Path to the local provider directory:
    _dataset_path: pathlib.Path

    # Path to the file (relative to local provider directory):
    _file_path: pathlib.Path

    # Size of the file:
    _size: int

    def __init__(self, dataset_path: os.PathLike, source_path: os.PathLike):
        self._dataset_path = pathlib.Path(dataset_path)
        self._file_path = pathlib.Path(source_path).relative_to(self._dataset_path)
        self._size = self.source_path.stat().st_size

    @property
    def source_path(self) -> pathlib.Path:
        """
        Returns:
            The full path to the source file.
        """
        return self._dataset_path.joinpath(self._file_path)

    @property
    def size(self) -> int:
        """
        Returns:
            The size of the file, in bytes.
        """
        return self._size

    def download(self, local_file: pathlib.Path):
        """
        Copy this file from the local provider directory to the local path.

        Args:
            local_file: Local path where the file should be copied.
        """
        shutil.copyfile(self.source_path, local_file)

    @property
    def relative_path(self) -> pathlib.Path:
        """
        Returns:
            The path of this file relative to the local provider directory
            and version it belongs.
        """
        return self._file_path


class LocalAsProvider(RemoteProvider):

    """
    The `LocalAsProvider` is a `Provider` associated to a local source of
    datasets.
    """

    # Local source path of dataset:
    _source_path: pathlib.Path
    _pbar: tqdm

    def __init__(self, root_folder: os.PathLike, source_folder: os.PathLike):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            source_folder: local source directory of datasets.
        """
        self._source_path = pathlib.Path(source_folder)
        super().__init__(root_folder, self._source_path.absolute().as_posix())

    def _is_available(self) -> bool:
        """
        Check if the local source directory exists.

        Returns:
            `True` the local source directory exists, `False` otherwize.
        """
        return self._source_path.exists()

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        """
        List the the local source files for the given dataset version.

        Args:
            name: Name of the dataset.
            version: Version of the dataset.

        Returns:
            A list of files for the local source dataset version, that can be copied
            using `RemoteFile.download`.
        """
        # Path to the dataset:
        dataset_path = self._source_path.joinpath(name, version)

        return [
            LocalFile(dataset_path, fpath)
            for fpath in dataset_path.rglob("*")
            if not fpath.is_dir()
        ]

    def _before_downloads(self, files: typing.List[RemoteFile]):
        # Compute the total volume of data to copy and initialize
        # a proper TQDM bar:
        total_file_size = 0
        for rfile in files:
            assert isinstance(rfile, LocalFile)
            total_file_size += rfile.size

        self._pbar = tqdm(
            total=total_file_size,
            desc="Copying... ",
            unit="bytes",
            unit_scale=True,
            unit_divisor=1024,
        )

    def _after_downloads(self, local_file: pathlib.Path):
        self._pbar.close()

    def _file_downloaded(self, file: RemoteFile, local_file: pathlib.Path):
        assert isinstance(file, LocalFile)
        self._pbar.update(file.size)

    def list_datasets(self) -> typing.List[str]:
        return self._remove_hidden_values(
            [f.name.strip("/") for f in self._source_path.iterdir()]
        )

    def list_versions(self, dataset: str) -> typing.List[str]:
        directory = self._source_path.joinpath(dataset)
        if not directory.exists():
            raise DatasetNotFoundError(dataset)

        return self._remove_hidden_values([f.name for f in directory.iterdir()])

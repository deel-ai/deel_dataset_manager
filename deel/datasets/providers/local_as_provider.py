# -*- encoding: utf-8 -*-

import os
import pathlib
import typing
import sys

from tqdm import tqdm, trange
from shutil import copy, copytree
from time import sleep
import threading

from .exceptions import DatasetNotFoundError

# from .remote_provider import RemoteFile andRemoteProvider
from .remote_provider import RemoteFile, RemoteProvider


class LocalFile(RemoteFile):

    """
    Representing a local file as local provider file.
    """

    # Path to the local provider directory:
    _source_path: str

    # Path to the file (relative to local provider directory):
    _file_path: str

    def __init__(self, dataset_path: str, file_path: str):
        self._source_path = dataset_path.rstrip("/")
        self._file_path = file_path.strip("/")

    def download(self, local_file: pathlib.Path):
        """
        Copy this file from the local provider directory to the local path.

        Args:
            local_file: Local path where the file should be copied.
        """

        source_file = pathlib.Path("{}/{}".format(self._source_path, self._file_path))
        if source_file.is_file() is True:
            copy(source_file, local_file)
        else:
            copytree(source_file, local_file)

    @property
    def relative_path(self) -> pathlib.Path:
        """
        Returns:
            The path of this file relative to the local provider directory
            and version it belongs.
        """
        return pathlib.Path(self._file_path)


class LocalAsProvider(RemoteProvider):

    """
    The `LocalAsProvider` is a `Provider` associated to a local source of
    datasets.
    """

    # Local source path of dataset:
    _source_path: str
    _pbar: tqdm
    _waiting_thread: threading.Thread

    def __init__(self, root_folder: os.PathLike, source_folder: str):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            source_folder: local source directory of datasets.
        """
        super().__init__(root_folder, source_folder)
        self._source_path = source_folder

    @property
    def remote_url(self) -> str:
        """
        Returns: The local source directory of datasets.
        """
        return self._source_path

    def _is_available(self) -> bool:
        """
        Check if the local source directory exists.

        Returns:
            `True` the local source directory exists, `False` otherwize.
        """
        return pathlib.Path(self._source_path).exists()

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
        files_path = "{}{}/{}/".format(self._source_path, name, version)
        directory = pathlib.Path(files_path)
        return [
            LocalFile(files_path, fpath.name)
            for fpath in directory.iterdir()
            if fpath.name.rstrip("/") != version
        ]

    # A waitng progress bar
    def waiting_bar(self):
        self._pbar = trange(
            100, file=sys.stdout, leave=False, unit_scale=True, desc="Copying..."
        )
        for i in self._pbar:
            sleep(0.1)

    def _before_downloads(self, files: typing.List[RemoteFile]):
        """
        Initialize a tqdm for download task.

        Args:
            List of files to be downloaded
        """
        self._waiting_thread = threading.Thread(target=self.waiting_bar)
        self._waiting_thread.start()

    def _after_downloads(self):
        """
        Close the initialized tqdm.
        """
        self._pbar.close()
        self._waiting_thread.join()

    def _file_downloaded(self, file: RemoteFile, local_file: pathlib.Path):
        """
        Increments tqdm progression.
        """
        # relaunch the waiting progress bar
        self._waiting_thread = threading.Thread(target=self.waiting_bar)
        self._waiting_thread.start()

    def list_datasets(self) -> typing.List[str]:
        """
        List the available datasets in the local dataset source.

        Returns:
            The list of datasets available in local source.
        """
        source = pathlib.Path(self._source_path)
        return self._remove_hidden_values([f.name.strip("/") for f in source.iterdir()])

    def list_versions(self, dataset: str) -> typing.List[str]:
        """
        List the available versions of the given dataset in the local dataset source.

        Returns:
            The list of available versions of the given dataset in
            the local dataset source.

        Raises:
            DatasetNotFoundError: If the given dataset does not exist.
        """
        # Check that the dataset exists:
        dataset_path = "{}{}/".format(self._source_path, dataset)
        directory = pathlib.Path(dataset_path)
        if not directory.exists():
            raise DatasetNotFoundError(dataset_path)

        return self._remove_hidden_values(
            [
                f.name.strip("/")
                for f in directory.iterdir()
                if f.name.strip("/") != dataset
            ]
        )

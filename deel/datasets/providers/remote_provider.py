# -*- encoding: utf-8 -*-

import abc
import gzip
import os
import pathlib
import shutil
import tarfile
import typing
import zipfile

from tqdm import tqdm

from . import logger
from .exceptions import (
    DatasetNotFoundError,
    VersionNotFoundError,
    DatasetVersionNotFoundError,
)
from .local_provider import LocalProvider


class FileModifier(abc.ABC):

    """
    Abstract class representing a modifier to apply to the file
    downloaded by the WebDAV provider.
    """

    def accept(self, file: pathlib.Path) -> bool:
        """
        Check if the given file can be modified by this modifier.

        Args:
            file: The file to check.

        Returns: True if the file can be modified, False otherwize.
        """
        pass

    def apply(self, file: pathlib.Path):
        """
        Apply this modifier to the given file.

        Args:
            file: The file to apply the modifier to.

        Raises:
            FileNotFoundError: If the file does not exists.
        """
        pass


class ZipExtractor(FileModifier):

    """
    Modifier that unzip files and delete them afterwards.
    """

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".zip"

    def apply(self, file: pathlib.Path):
        # Extract using zipfile then unlink:
        with zipfile.ZipFile(file, "r") as zp:
            zp.extractall(file.parent)
        file.unlink()


class TarZExtractor(FileModifier):

    """
    Modifier that extract files from tar archives, with or
    without comrpession and delete them afterwards.

    See the `tarfile` library for the list of supported compression
    methods.
    """

    def accept(self, file: pathlib.Path) -> bool:
        # We accept .tgz, .tar and .tar.gz
        return file.suffix in [".tgz", ".tbz2", ".txz", ".tar"] or (
            len(file.suffixes) > 1
            and file.suffixes[-2] == ".tar"
            and file.suffixes[-1] in [".gz", ".bz2", ".xz"]
        )

    def apply(self, file: pathlib.Path):
        # Extract using tarfile then unlink:
        with tarfile.open(file, "r") as tp:
            tp.extractall(file.parent)
        file.unlink()


class GzExtractor(FileModifier):

    """
    Modifier that extract files from gz archives and delete
    them afterwards.
    """

    # Size of the buffer to use for extraction:
    _buffer_size = 4096

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".gz" and file.with_suffix("").suffix != ".tar"

    def apply(self, file: pathlib.Path):

        # Extract the content using gzip then remove the file:
        with gzip.open(file, "rb") as zp, open(file.with_suffix(""), "wb") as fp:
            pbar = tqdm(
                desc="Extracting " + file.name,
                unit="bytes",
                unit_scale=True,
                unit_divisor=1024,
            )
            while True:
                data = zp.read(self._buffer_size)
                if not data:
                    break
                fp.write(data)
                pbar.update(len(data))
            pbar.close()

        file.unlink()


class RemoteFile(object):

    """
    Abstraction representing a remote file.
    """

    @abc.abstractmethod
    def download(self, local_file: pathlib.Path):
        """
        Download this file from the remote storage to the local path.

        Args:
            local_file: Local path where the file should be downloaded.
        """
        pass

    @property
    @abc.abstractmethod
    def relative_path(self) -> pathlib.Path:
        """
        Returns:
            The path of this file relative to the dataset and version it belongs.
        """
        pass


class RemoteProvider(LocalProvider):

    """
    The `RemoteProvider` extends `LocalProvider` by fetching datasets
    from a remote server if they are not found on the local storage.

    If a dataset is not found locally (or a force download is required), the
    provider will first downloads all the files corresponding to the given dataset,
    and then extract all archived files (.zip, .gz, .tgz) in the local folder.
    """

    # Remote server URL:
    _remote_url: str

    # List of modifiers to apply to the files:
    modifiers: typing.List[FileModifier] = [
        ZipExtractor(),
        TarZExtractor(),
        GzExtractor(),
    ]

    def __init__(self, root_folder: os.PathLike, remote_url: str):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the WebDAV server.
        """
        super().__init__(root_folder)
        self._remote_url = remote_url

    @property
    def remote_url(self) -> str:
        """
        Returns: The remote URL from where the datasets are fetched.
        """
        return self._remote_url

    def local_provider(self) -> LocalProvider:
        """
        Create and returns a `LocalProvider` corresponding to the local
        storage for this provider.

        Returns:
            A `LocalProvider` that fetches datasets from the local folder this
            provider stores the datasets to.
        """
        return LocalProvider(self.root_folder)

    @abc.abstractmethod
    def _is_available(self) -> bool:
        """
        Check if the remote server is available.

        Returns:
            `True` if the remote server is available, `False` otherwize.
        """
        pass

    @abc.abstractmethod
    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        """
        List the remote files for the given dataset version.

        Args:
            name: Name of the dataset.
            version: Version of the dataset.

        Returns:
            A list of files for the remote dataset version, that can be downloaded
            using `RemoteFile.download`.
        """
        pass

    def _get_remote_version(self, name: str, version: str = "latest") -> str:
        """
        Retrieve the remote version corresponding to the given dataset.

        Args:
            name: Name of the dataset.
            version: Version selector for the dataset.

        Returns:
            The remote version corresponding to this dataset.

        Raises:
            DatasetNotFoundError: If the given remote dataset was not found.
            DatasetVersionNotFoundError: If the given version did not match any
                version in the remote repository.
        """

        # List of remote versions:
        remote_versions: typing.List[str] = []

        # Check the remote client and list the versions:
        if self._is_available() and name in self.list_datasets():
            remote_versions = self.list_versions(name)
        else:
            raise DatasetNotFoundError(name)

        try:
            return self.get_version(version, remote_versions)
        except VersionNotFoundError:
            raise DatasetVersionNotFoundError(name, version)

    def get_folder(
        self,
        name: str,
        version: str = "latest",
        force_update: bool = False,
        returns_version: bool = False,
    ) -> typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, str]]:

        # Find the local path (if any):
        local_path: typing.Optional[pathlib.Path] = None
        try:
            local_path, local_version = super().get_folder(  # type: ignore
                name, version, returns_version=True
            )
        except DatasetNotFoundError:
            pass

        try:
            remote_version = self._get_remote_version(name, version)

        except DatasetNotFoundError as e:

            # Remote version not found, and there is no local path, we throw:
            if local_path is None:
                raise e

            # Otherwize we warn user that dataset might be outdated, and return
            # the local path:
            logger.warning(
                "Remote dataset not found, using local one, version might be outdated."
            )

            if returns_version:
                return local_path, local_version
            else:
                return local_path

        # Create the local folder using the exact version:
        local_exact_path = self._make_folder(name, remote_version)

        # If the local path is exact and a force update is not required,
        # we simply return:
        if local_path == local_exact_path and not force_update:
            if returns_version:
                return local_exact_path, remote_version
            else:
                return local_exact_path

        if local_exact_path.exists():
            shutil.rmtree(local_exact_path, ignore_errors=True)
        local_exact_path.mkdir(parents=True, exist_ok=True)

        # List the files in the remote folder:
        files = self._list_remote_files(name, remote_version)

        # Download all the files and apply the modifier:
        for remote_file in files:

            # The local file:
            local_file = local_exact_path.joinpath(remote_file.relative_path)

            # Download the file:
            remote_file.download(local_file)

            # Apply the modifiers:
            for modifier in self.modifiers:
                if modifier.accept(local_file):
                    modifier.apply(local_file)

        if returns_version:
            return local_exact_path, remote_version
        else:
            return local_exact_path


class RemoteSingleFileProvider(RemoteProvider):

    """
    The `RemoteSingleFileProvider` extends `RemoteProvider` and should be used
    to fetch files from custom web servers (HTTP, FTP) that only provide a single
    file. The only methods that should be implemented are `_is_available` and
    `_list_remote_files`.`

    The goal of this class is mainly to be used to allow the creation of datasets
    from publicly available files.
    """

    # Name and version of the dataset corresponding to the remote file:
    _name: str
    _version: str

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        name: str,
        version: str = "1.0.0",
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the WebDAV server.
            name: Name of the dataset corresponding to the remote file.
            version: Version of the dataset corresponding to the remote file.
        """
        super().__init__(root_folder, remote_url)

        self._name = name
        self._version = version

    def list_datasets(self) -> typing.List[str]:
        return [self._name]

    def list_versions(self, dataset: str) -> typing.List[str]:
        return [self._version]

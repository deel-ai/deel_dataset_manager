# -*- encoding: utf-8 -*-

import abc
import gzip
import os
import pathlib
import shutil
import tarfile
import typing
import zipfile

from . import logger
from .exceptions import (
    DatasetNotFoundError,
    VersionNotFoundError,
    DatasetVersionNotFoundError,
)
from .local_provider import LocalProvider


class FileModifier(abc.ABC):

    """ Abstract class representing a modifier to apply to the file
    downloaded by the WebDAV provider. """

    def accept(self, file: pathlib.Path) -> bool:
        """ Check if the given file can be modified by this modifier.

        Args:
            file: The file to check.

        Returns: True if the file can be modified, False otherwize.
        """
        pass

    def apply(self, file: pathlib.Path):
        """ Apply this modifier to the given file.

        Args:
            file: The file to apply the modifier to.

        Raises:
            FileNotFoundError: If the file does not exists.
        """
        pass


class ZipExtractor(FileModifier):

    """ Modifier that unzip files and delete them afterwards. """

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".zip"

    def apply(self, file: pathlib.Path):
        # Extract using zipfile then unlink:
        with zipfile.ZipFile(file, "r") as zp:
            zp.extractall(file.parent)
        file.unlink()


class TarGzExtractor(FileModifier):

    """ Modifier that extract files from tar/gz archives and delete
    them afterwards. """

    def accept(self, file: pathlib.Path) -> bool:
        # We accept .tgz, .tar and .tar.gz
        return file.suffix in [".tgz", ".tar"] or file.suffixes == [".tar", ".gz"]

    def apply(self, file: pathlib.Path):
        # Extract using tarfile then unlink:
        with tarfile.open(file, "r") as tp:
            tp.extractall(file.parent)
        file.unlink()


class GzExtractor(FileModifier):

    """ Modifier that extract files from gz archives and delete
    them afterwards. """

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".gz" and file.with_suffix("").suffix != ".tar"

    def apply(self, file: pathlib.Path):
        # Extract the content using gzip then remove the file:
        with gzip.open(file, "rb") as zp, gzip.open(file.with_suffix(""), "wb") as fp:
            fp.write(zp.read())
        file.unlink()


class RemoteFile(object):

    """ Abstraction representing a remote file. """

    @abc.abstractmethod
    def download(self, local_file: pathlib.Path):
        """ Download this file from the remote storage to the local path.

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

    """ The `RemoteProvider` extends `LocalProvider` by fetching datasets
    from a remote server if they are not found on the local storage.

    If a dataset is not found locally (or a force download is required), the
    provider will first downloads all the files corresponding to the given dataset,
    and then extract all archived files (.zip, .gz, .tgz) in the local folder. """

    # Remote server URL:
    _remote_url: str

    # List of modifiers to apply to the files:
    modifiers: typing.List[FileModifier] = [
        ZipExtractor(),
        TarGzExtractor(),
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
        """ Returns: The remote URL from where the datasets are fetched. """
        return self._remote_url

    def local_provider(self) -> LocalProvider:
        """ Create and returns a `LocalProvider` corresponding to the local
        storage for this provider.

        Returns:
            A `LocalProvider` that fetches datasets from the local folder this
            provider stores the datasets to.
        """
        return LocalProvider(self.root_folder)

    @abc.abstractmethod
    def _is_available(self) -> bool:
        """ Check if the remote server is available.

        Returns:
            `True` if the remote server is available, `False` otherwize.
        """

    @abc.abstractmethod
    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        """ List the remote files for the given dataset version.

        Args:
            name: Name of the dataset.
            version: Version of the dataset.

        Returns:
            A list of files for the remote dataset version, that can be downloaded
            using `RemoteFile.download`.
        """
        pass

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:

        # Find the local path (if any):
        local_path: typing.Optional[pathlib.Path] = None
        try:
            local_path = super().get_folder(name, version)
        except DatasetNotFoundError:
            pass

        # List of remote versions:
        remote_versions: typing.List[str] = []

        # Check the remote client and list the versions:
        if self._is_available() and name in self.list_datasets():
            remote_versions = self.list_versions(name)

        # Check failed and we have no local version, we throw:
        elif local_path is None:
            raise DatasetNotFoundError(name)

        # We find the best matching version (if the check failed on the
        # the previous if, remote_versions is empty, and VersionNotFoundError
        # will be thrown):
        try:
            remote_version = self.get_version(version, remote_versions)
        except VersionNotFoundError:

            # Remote version not found, and there is no local path, we throw:
            if local_path is None:
                raise DatasetVersionNotFoundError(name, version)

            # Otherwize we warn user that dataset might be outdated, and return
            # the local path:
            logger.warning(
                "Remote dataset not found, using local one, version might be outdated."
            )
            return local_path

        # Create the local folder using the exact version:
        local_exact_path = self._make_folder(name, remote_version)

        # If the local path is exact and a force update is not required,
        # we simply return:
        if local_path == local_exact_path and not force_update:
            return local_path

        if local_exact_path.exists():
            shutil.rmtree(local_exact_path)
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

        return local_exact_path

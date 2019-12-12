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
from webdav3.client import Client
from webdav3.urn import Urn

from . import logger
from .exceptions import (
    DatasetNotFoundError,
    VersionNotFoundError,
    DatasetVersionNotFoundError,
)
from .local_provider import LocalProvider


class WebDavAuthenticator(abc.ABC):

    """ Base class for WebDAV authenticators.

    Authenticator classes are used for dispatching and storing eventual parameters. """

    pass


class WebDavSimpleAuthenticator(WebDavAuthenticator):

    """ Authenticator for a simple HTTP authentication with a username and a
    password. """

    # Username and password:
    _username: str
    _password: str

    def __init__(self, username: str, password: str):
        """
        Args:
            username: Username to use for authentication.
            password: Password to use for authentication.
        """
        self._username = username
        self._password = password

    @property
    def username(self):
        """ Returns: The username to use for authentication. """
        return self._username

    @property
    def password(self):
        """ Returns: The password to use for authentication. """
        return self._password


class WebDavFileModifier(abc.ABC):

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


class WebDavZipExtractor(WebDavFileModifier):

    """ Modifier that unzip files and delete them afterwards. """

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".zip"

    def apply(self, file: pathlib.Path):
        # Extract using zipfile then unlink:
        with zipfile.ZipFile(file, "r") as zp:
            zp.extractall(file.parent)
        file.unlink()


class WebDavTarGzExtractor(WebDavFileModifier):

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


class WebDavGzExtractor(WebDavFileModifier):

    """ Modifier that extract files from gz archives and delete
    them afterwards. """

    def accept(self, file: pathlib.Path) -> bool:
        return file.suffix == ".gz" and file.with_suffix("").suffix != ".tar"

    def apply(self, file: pathlib.Path):
        # Extract the content using gzip then remove the file:
        with gzip.open(file, "rb") as zp, gzip.open(file.with_suffix(""), "wb") as fp:
            fp.write(zp.read())
        file.unlink()


class WebDavProvider(LocalProvider):

    """ The `WebDavProvider` extends `LocalProvider` by fetching datasets
    from a remote server if they are not found on the local storage. The remote
    server may or may not require authentication.

    If a dataset is not found locally (or a force download is required), the
    provider will first downloads all the files corresponding to the given dataset,
    and then extract all archived files (.zip, .gz, .tgz) in the local folder. """

    # Remote server URL:
    _remote_url: str

    # Authenticator to use:
    _authenticator: typing.Optional[WebDavAuthenticator]

    # The WebDAV client:
    _client: Client

    # List of modifiers to apply to the files:
    modifiers: typing.List[WebDavFileModifier] = [
        WebDavZipExtractor(),
        WebDavTarGzExtractor(),
        WebDavGzExtractor(),
    ]

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        authenticator: typing.Optional[WebDavAuthenticator] = None,
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the WebDAV server.
            authenticator: Authenticator to use.
        """
        super().__init__(root_folder)
        self._remote_url = remote_url
        self._authenticator = authenticator

        # Create the WebDAV client:
        options = {"webdav_hostname": self._remote_url}
        if isinstance(self._authenticator, WebDavSimpleAuthenticator):
            options["webdav_login"] = self._authenticator.username
            options["webdav_password"] = self._authenticator.password
        self._client = Client(options)

    def _download_file(self, remote_file: str, local_file: pathlib.Path):
        """ Download the given file using the given client.

        Args:
            remote_file: Relative path to the remote file to download (without URL).
            local_file: Local path where the file should be downloaded.
        """

        # Retrieve information (size) of the file:
        file_info = self._client.info(remote_file)
        file_size = int(file_info["size"])

        # The code below is taken from webdav3.Client.download_file, and is adapted
        # for progress.
        urn = Urn(remote_file)

        logger.info("Downloading {}... ".format(local_file))
        with open(local_file, "wb") as fp:
            response = self._client.execute_request("download", urn.quote())

            # TODO: Remove logging if logger is disabled:
            pbar = tqdm(
                total=file_size,
                desc=local_file.parts[-1],
                unit="bytes",
                unit_scale=True,
                unit_divisor=1024,
            )
            for block in response.iter_content(1024):
                fp.write(block)
                pbar.update(len(block))
            pbar.close()

    def list_datasets(self) -> typing.List[str]:
        return [name for name in self._client.list()]

    def list_versions(self, dataset: str) -> typing.List[str]:

        # Check that the dataset exists:
        remote_path = dataset + "/"
        if not self._client.check(remote_path):
            raise DatasetNotFoundError(remote_path)

        return [name for name in self._client.list(remote_path)]

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:

        # Find the local path (if any):
        local_path: typing.Optional[pathlib.Path] = None
        try:
            local_path = super().get_folder(name, version)
        except DatasetNotFoundError:
            pass

        # Remote dataset path (must have a trailing /):
        remote_dataset = name + "/"

        # List of remote versions:
        remote_versions: typing.List[str] = []

        # Check the remote client and list the versions:
        if self._client.check(remote_dataset):
            remote_versions = [v.strip("/") for v in self._client.list(remote_dataset)]

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
        local_exact_path = super()._make_folder(name, remote_version)

        # If the local path is exact and a force update is not required,
        # we simply return:
        if local_path == local_exact_path and not force_update:
            return local_path

        if local_exact_path.exists():
            shutil.rmtree(local_exact_path)
        local_exact_path.mkdir(parents=True, exist_ok=True)

        # List the files in the remote folder:
        remote_location = remote_dataset + remote_version + "/"
        files = self._client.list(remote_location)

        # Download all the files and apply the modifier:
        for file in files:

            # The local file:
            local_file = local_exact_path.joinpath(file)

            # Download the file:
            self._download_file(remote_location + file, local_file)

            # Apply the modifiers:
            for modifier in self.modifiers:
                if modifier.accept(local_file):
                    modifier.apply(local_file)

        return local_exact_path

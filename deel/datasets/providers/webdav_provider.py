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
from .local_provider import LocalProvider, DatasetNotFoundError


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

    def _download_file(
        self, webdav_client: Client, remote_file: str, local_file: pathlib.Path
    ):
        """ Download the given file using the given client.

        Args:
            webdav_client: Client to use to download the file.
            remote_file: Relative path to the remote file to download (without URL).
            local_file: Local path where the file should be downloaded.
        """

        # Retrieve information (size) of the file:
        file_info = webdav_client.info(remote_file)
        file_size = int(file_info["size"])

        # The code below is taken from webdav3.Client.download_file, and is adapted
        # for progress.
        urn = Urn(remote_file)

        logger.info("Downloading {}... ".format(local_file))
        with open(local_file, "wb") as fp:
            response = webdav_client.execute_request("download", urn.quote())

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

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:

        # If download is not require, try to retrieve the local dataset:
        if not force_update:

            # Try to retrieve the local dataset (do nothing on except):
            try:
                return super().get_folder(name, version)
            except DatasetNotFoundError:
                pass

        # Create the WebDAV client:
        options = {"webdav_hostname": self._remote_url}
        if isinstance(self._authenticator, WebDavSimpleAuthenticator):
            options["webdav_login"] = self._authenticator.username
            options["webdav_password"] = self._authenticator.password
        client = Client(options)

        # Check that the remote dataset exists (must have a trailing /):
        remote_dataset = name + "/" + version + "/"
        if not client.check(remote_dataset):
            raise DatasetNotFoundError(name, version)

        # Create the local folder if it does not exists:
        local_folder = self._make_folder(name, version)
        if local_folder.exists():
            shutil.rmtree(local_folder)
        local_folder.mkdir(parents=True, exist_ok=True)

        # List the files in the remote folder:
        files = client.list(remote_dataset)

        # Download all the files and apply the modifier:
        for file in files:

            # The local file:
            local_file = local_folder.joinpath(file)

            # Download the file:
            self._download_file(client, remote_dataset + file, local_file)

            # Apply the modifiers:
            for modifier in self.modifiers:
                if modifier.accept(local_file):
                    modifier.apply(local_file)

        return local_folder

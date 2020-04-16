# -*- encoding: utf-8 -*-

import os
import typing

from ftplib import FTP, error_temp
from pathlib import Path
from tqdm import tqdm

from . import logger
from .exceptions import DatasetNotFoundError
from .remote_provider import RemoteFile, RemoteProvider, RemoteSingleFileProvider


class FtpSimpleAuthenticator:

    """ Authenticator for a simple FTP authentication with a
    username and a password. """

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


class FtpRemoteFile(RemoteFile):

    """ Class representing a remote file for the FTP provider. """

    # The FTP client:
    _client: FTP

    # Remote path of the file from the ROOT of the FTP server::
    _remote_path: Path

    # Local path of the file relative to the dataset folder:
    _local_path: Path

    def __init__(self, client: FTP, remote_path: Path, local_path: Path):
        """
        Args:
            client: The FTP client (used for download).
            remote_path: Remote path to the dataset file, relative the root of
                the FTP server..
            local_path: Local path to the file of the dataset, relative to the dataset
                folder.
        """
        self._client = client
        self._remote_path = remote_path
        self._local_path = local_path

    def download(self, local_file: Path):

        # Convert the filename to a string:
        filename = self._remote_path.as_posix()

        # Retrive the file size:
        file_size = self._client.size(filename)

        logger.info("Downloading {}... ".format(local_file))
        with open(local_file, "wb") as fp:

            # TODO: Remove logging if logger is disabled:
            pbar = tqdm(
                total=file_size,
                desc=self._local_path.parts[-1],
                unit="bytes",
                unit_scale=True,
                unit_divisor=1024,
            )

            def callback(block):
                fp.write(block)
                pbar.update(len(block))

            self._client.retrbinary("RETR {}".format(filename), callback)

            pbar.close()

    @property
    def relative_path(self) -> Path:
        return self._local_path


class FtpProvider(RemoteProvider):

    """ The `FtpProvider` is a `RemoteProvider` associated to a FTP
    server. """

    # The FTP client:
    _client: FTP

    # Remote path to the folder containing the datasets:
    _remote_path: Path

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        authenticator: typing.Optional[FtpSimpleAuthenticator] = None,
        **kwargs
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the WebDAV server.
            authenticator: Authenticator to use.
            **kwargs: Extra arguments for the `FTP` constructor.
        """
        super().__init__(root_folder, remote_url)

        # Create the FTP client:
        if authenticator is not None:
            kwargs.update(
                {"user": authenticator.username, "passwd": authenticator.password}
            )

        # Remove the ftp(s):// prefix:
        if remote_url.find("://") != -1:
            remote_url = remote_url[remote_url.find("://") + 3 :]

        # Split the URL to get the root FTP server and the filepath:
        parts = remote_url.split("/")
        remote_url = parts[0]

        self._client = FTP(remote_url, **kwargs)
        self._remote_path = Path(*parts[1:])

        # Switch to binary mode:
        self._client.sendcmd("type i")

    def __exit__(self, *args):
        return self._client.__exit__(*args)

    def _is_available(self) -> bool:
        # The provider is always available is the constructor did
        # not throw.
        return True

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        # Path to the dataset:
        dataset_path = self._remote_path.joinpath(name, version)

        return [
            FtpRemoteFile(self._client, dataset_path, dataset_path.joinpath())
            for fpath in self._remove_hidden_values(
                self._client.nlst(dataset_path.as_posix())
            )
        ]

    def list_datasets(self) -> typing.List[str]:
        return self._remove_hidden_values(
            [
                name.strip("/")
                for name in self._client.nlst(self._remote_path.as_posix())
            ]
        )

    def list_versions(self, dataset: str) -> typing.List[str]:

        # Check that the dataset exists:
        remote_path = self._remote_path.joinpath(dataset)

        try:
            return self._remove_hidden_values(
                [name.strip("/") for name in self._client.nlst(remote_path.as_posix())]
            )
        except error_temp:
            raise DatasetNotFoundError(dataset)


class FtpSingleFileProvider(RemoteSingleFileProvider, FtpProvider):

    """ The `FtpProvider` is a `RemoteProvider` associated to a FTP server.

    This provider currently does not supported encrypted connection. """

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        name: str,
        version: str = "1.0.0",
        authenticator: typing.Optional[FtpSimpleAuthenticator] = None,
        **kwargs
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the file to serve.
            name: Name of the dataset corresponding to the remote file.
            version: Version of the dataset corresponding to the remote file.
            authenticator: Authenticator to use.
            **kwargs: Extra arguments for the `FTP` constructor.
        """
        RemoteSingleFileProvider.__init__(self, root_folder, remote_url, name, version)
        FtpProvider.__init__(self, root_folder, remote_url, authenticator, **kwargs)

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        return [
            FtpRemoteFile(self._client, self._remote_path, Path(self._remote_path.name))
        ]
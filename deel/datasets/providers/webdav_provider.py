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
import abc
import os
import pathlib
import re
import typing

from tqdm import tqdm
from webdav3.client import Client
from webdav3.exceptions import WebDavException
from webdav3.urn import Urn

from . import logger
from .exceptions import DatasetNotFoundError
from .remote_provider import RemoteFile, RemoteProvider


class WebDavAuthenticator(abc.ABC):

    """
    Base class for WebDAV authenticators.

    Authenticator classes are used for dispatching and storing eventual parameters.
    """

    pass


class WebDavSimpleAuthenticator(WebDavAuthenticator):

    """
    Authenticator for a simple HTTP authentication with a username and a
    password.
    """

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
        """
        Returns: The username to use for authentication.
        """
        return self._username

    @property
    def password(self):
        """
        Returns: The password to use for authentication.
        """
        return self._password


class WebDavRemoteFile(RemoteFile):

    """
    Class representing a remote file for the WebDAV provider.
    """

    # The WebDAV client:
    _client: Client

    # Path to the dataset (relative to the root of the server):
    _dataset_path: str

    # Path to the file (relative to the dataset):
    _file_path: str

    def __init__(self, client: Client, dataset_path: str, file_path: str):
        """
        Args:
            client: The WebDAV client (used for download).
            dataset_path: Path to the dataset, relative the root of the server.
            file_path: Path to the file of the dataset, relative to the dataset path.
        """
        self._client = client
        self._dataset_path = dataset_path.rstrip("/")
        self._file_path = file_path.strip("/")

    def download(self, local_file: pathlib.Path):

        remote_file = "{}/{}".format(self._dataset_path, self._file_path)

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

    @property
    def relative_path(self) -> pathlib.Path:
        """
        Returns:
            The path of this file relative to the dataset and version it belongs.
        """
        return pathlib.Path(self._file_path)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "WebDavRemoteFile at {}//{}".format(self._dataset_path, self._file_path)


class WebDavProvider(RemoteProvider):

    """
    The `WebDavProvider` is a `RemoteProvider` associated to a WebDAV
    server.
    """

    # Version regex (to filter folders):
    VERSION_REGEX: typing.Pattern = re.compile("[0-9]+[.][0-9]+[.][0-9]+")

    # Authenticator to use:
    _authenticator: typing.Optional[WebDavAuthenticator]

    # Relative path from the root of the WebDAV server:
    _remote_path: str

    # The WebDAV client:
    _client: Client

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        remote_path: str = "",
        authenticator: typing.Optional[WebDavAuthenticator] = None,
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the WebDAV server.
            authenticator: Authenticator to use.
        """
        super().__init__(root_folder, remote_url)

        # WebDAV specific members:
        self._authenticator = authenticator

        # Remote path from the root of the webdav folder:
        self._remote_path = remote_path
        if self._remote_path and not self._remote_path.endswith("/"):
            self._remote_path += "/"

        # Create the WebDAV client:
        options = {"webdav_hostname": self._remote_url}
        if isinstance(self._authenticator, WebDavSimpleAuthenticator):
            options["webdav_login"] = self._authenticator.username
            options["webdav_password"] = self._authenticator.password
        self._client = Client(options)

    def _is_available(self) -> bool:
        try:
            return self._client.check()  # type: ignore
        except WebDavException:
            return False

    def _is_dataset_folder(self, name):
        if self._remote_path:
            relative_root = self._remote_path.rstrip("/").split("/")[-1]
        else:
            relative_root = self._remote_url.rstrip("/").split("/")[-1]

        if name.strip("/") == relative_root:
            return False

        return any(self.VERSION_REGEX.match(v) for v in self.list_versions(name))

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        # Path to the dataset:
        dataset_path = "{}{}/{}/".format(self._remote_path, name, version)
        return [
            WebDavRemoteFile(self._client, dataset_path, fpath)
            for fpath in self._client.list(dataset_path)
            if fpath.rstrip("/") != version
        ]

    def list_datasets(self) -> typing.List[str]:
        return self._remove_hidden_values(
            [
                name.strip("/")
                for name in self._client.list(self._remote_path)
                if self._is_dataset_folder(name)
            ]
        )

    def list_versions(self, dataset: str) -> typing.List[str]:

        # Check that the dataset exists:
        remote_path = "{}{}/".format(self._remote_path, dataset)
        if not self._client.check(remote_path):
            raise DatasetNotFoundError(remote_path)

        return self._remove_hidden_values(
            [
                name.strip("/")
                for name in self._client.list(remote_path)
                if name.strip("/") != dataset
            ]
        )

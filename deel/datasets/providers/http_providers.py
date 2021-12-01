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
import typing
import urllib.parse
import urllib.request

from tqdm import tqdm

from . import logger
from .remote_provider import RemoteFile, RemoteProvider


class HttpSimpleAuthenticator:

    """
    Authenticator for a simple HTTP authentication with a
    username and a password.
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


class HttpRemoteFile(RemoteFile):

    """
    Class representing a remote file for the WebDAV provider.
    """

    # The remote URL of the file::
    _remote_url: str

    # Path to the file in the dataset folder:
    _relative_path: pathlib.Path

    def __init__(self, remote_url: str, relative_path: pathlib.Path):
        """
        Args:
            remote_url: Remote URL of the file..
            relative_path: Relative path to the file from the dataset
                folder.
        """
        self._remote_url = remote_url
        self._relative_path = relative_path

    def download(self, local_file: pathlib.Path):

        conn = urllib.request.urlopen(self._remote_url)

        # Retrieve information (size) of the file:
        file_size = int(conn.getheader("Content-Length", 0))

        logger.info("Downloading {}... ".format(local_file))
        with open(local_file, "wb") as fp:

            # TODO: Remove logging if logger is disabled:
            pbar = tqdm(
                total=None if file_size == 0 else file_size,
                desc=local_file.parts[-1],
                unit="bytes",
                unit_scale=True,
                unit_divisor=1024,
            )

            while True:
                data = conn.read(1024)
                if not data:
                    break
                fp.write(data)
                pbar.update(len(data))
            pbar.close()

        conn.close()

    @property
    def relative_path(self) -> pathlib.Path:
        return self._relative_path


class HttpMultiFilesProvider(RemoteProvider):

    """
    This provider is a `RemoteProvider` that can serve a list of
    files over the HTTP protocol.
    """

    # Each remote URL, including credentials:
    _full_url_list: typing.List[str] = []

    # Name and version of the dataset corresponding to the remote file:
    _name: str
    _version: str

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url_list: typing.List[str],
        name: str,
        version: str = "1.0.0",
        authenticator: typing.Optional[HttpSimpleAuthenticator] = None,
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the file to serve.
            name: Name of the dataset corresponding to the remote file.
            version: Version of the dataset corresponding to the remote file.
            authenticator: Authenticator to use.
        """
        super().__init__(root_folder, remote_url_list[0])

        # Create the WebDAV client:
        for remote_url in remote_url_list:
            if authenticator is not None:
                remote_url = "{}:{}@{}".format(
                    urllib.parse.quote(authenticator.username, safe=""),
                    urllib.parse.quote(authenticator.password, safe=""),
                    remote_url,
                )
            self._full_url_list.append(remote_url)

        self._remote_version = version
        self._name = name
        self._version = version

    def _is_available(self) -> bool:
        for full_url in self._full_url_list:
            with urllib.request.urlopen(full_url) as fp:
                if fp.code == 200:
                    pass
                else:
                    return False
        return True

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        # Path to the dataset:
        return [
            HttpRemoteFile(full_url, pathlib.Path(full_url.split("/")[-1]))
            for full_url in self._full_url_list
        ]

    def list_datasets(self) -> typing.List[str]:
        return [self._name]

    def list_versions(self, dataset: str) -> typing.List[str]:
        return [self._version]


class HttpSingleFileProvider(HttpMultiFilesProvider):

    """
    This provider is a `RemoteProvider` that can only serve a single
    file over the HTTP protocol.
    """

    def __init__(
        self,
        root_folder: os.PathLike,
        remote_url: str,
        name: str,
        version: str = "1.0.0",
        authenticator: typing.Optional[HttpSimpleAuthenticator] = None,
    ):
        """
        Args:
            root_folder: Root folder to look-up datasets.
            remote_url: Remote URL of the file to serve.
            name: Name of the dataset corresponding to the remote file.
            version: Version of the dataset corresponding to the remote file.
            authenticator: Authenticator to use.
        """
        super().__init__(
            root_folder,
            [
                remote_url,
            ],
            name,
            version,
        )

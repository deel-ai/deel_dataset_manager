# -*- encoding: utf-8 -*-

import os
import pathlib
import typing
import urllib.parse
import urllib.request

import numpy as np
import mnist
from PIL import Image
from tqdm import tqdm

from . import logger
from .remote_provider import RemoteFile, RemoteProvider, RemoteSingleFileProvider


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


class HttpSingleFileProvider(RemoteSingleFileProvider):

    """
    This provider is a `RemoteProvider` that can only serve a single
    file over the HTTP protocol.
    """

    # The remote URL, including credentials:
    _full_url: str

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
            remote_url,
            name,
            version,
        )

        # Create the WebDAV client:
        if authenticator is not None:
            remote_url = "{}:{}@{}".format(
                urllib.parse.quote(authenticator.username, safe=""),
                urllib.parse.quote(authenticator.password, safe=""),
                remote_url,
            )

        self._remote_version = version
        self._full_url = remote_url

    def _is_available(self) -> bool:
        with urllib.request.urlopen(self._full_url) as fp:
            return fp.code == 200  # type: ignore

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        # Path to the dataset:
        return [
            HttpRemoteFile(self._full_url, pathlib.Path(self._full_url.split("/")[-1]))
        ]


class HttpProvider(RemoteProvider):

    """
    This provider is a `RemoteProvider` that can serve a list of
    files over the HTTP protocol.
    """

    # Each remote URL, including credentials:
    _full_url_list: typing.List[str] = []

    remote_url_list: typing.List[str]

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
            print(" ====> remote_url {}".format(remote_url))
            if authenticator is not None:
                remote_url = "{}:{}@{}".format(
                    urllib.parse.quote(authenticator.username, safe=""),
                    urllib.parse.quote(authenticator.password, safe=""),
                    remote_url,
                )
            self._full_url_list.append(remote_url)

        self.remote_url_list = remote_url_list
        self._remote_version = version
        self._name = name
        self._version = version

    def _convert_mnist_dataset(
        self,
        data_type: str,
        local_file: pathlib.Path,
        images: typing.List,
        labels: typing.List,
    ):
        train_dir = local_file.joinpath(data_type)
        os.makedirs(train_dir, exist_ok=True)
        for i in range(0, 10):
            os.makedirs(train_dir.joinpath(str(i)), exist_ok=True)

        label_iter = iter(labels)
        numImages = len(images)

        images_iterator = iter(images)
        with tqdm(
            total=len(images),
            desc="convert {} images".format(data_type),
        ) as pbar:
            for image in range(0, numImages):
                im = next(images_iterator)
                lab = next(label_iter)
                # create a np array to save the image
                im = np.array(im, dtype="uint8")
                im = im.reshape(28, 28)
                im = Image.fromarray(im)

                dest = train_dir.joinpath(
                    str(lab), "{}_{}.bmp".format(data_type, image)
                )
                im.save(dest, "bmp")
                pbar.update(1)

        pbar.close()

    def unpickle(self, file: pathlib.Path):
        import pickle

        with open(file, "rb") as fo:
            dict = pickle.load(fo, encoding="bytes")
            return dict

    def _is_available(self) -> bool:
        for full_url in self._full_url_list:
            with urllib.request.urlopen(full_url) as fp:
                if fp.code == 200:
                    print("_is_available {}".format(full_url))
                    pass
                else:
                    return False
        print("_is_available True")
        return True

    def _list_remote_files(self, name: str, version: str) -> typing.List[RemoteFile]:
        # Path to the dataset:
        print(
            "_list_remote_files {}".format(
                pathlib.Path(self._full_url_list[0].split("/")[-1])
            )
        )
        return [
            HttpRemoteFile(full_url, pathlib.Path(full_url.split("/")[-1]))
            for full_url in self._full_url_list
        ]

    def list_datasets(self) -> typing.List[str]:
        return [self._name]

    def list_versions(self, dataset: str) -> typing.List[str]:
        return [self._version]

    def _after_downloads(self, local_file: pathlib.Path):
        """
        Post-processing of dowloaded dataset.
        Case of MNIST dataset save images in corresponding label directory
        """
        if self._name == "ood":
            mnistdata = mnist.MNIST(local_file)
            images, labels = mnistdata.load_training()
            self._convert_mnist_dataset("train", local_file, images, labels)
            images, labels = mnistdata.load_testing()
            self._convert_mnist_dataset("test", local_file, images, labels)
            os.remove(local_file.joinpath("train-images-idx3-ubyte"))
            os.remove(local_file.joinpath("train-labels-idx1-ubyte"))
            os.remove(local_file.joinpath("t10k-images-idx3-ubyte"))
            os.remove(local_file.joinpath("t10k-labels-idx1-ubyte"))

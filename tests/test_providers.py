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
""" Tests for providers implementation"""
import ftplib
import os
import pathlib
import typing

import pytest

from deel.datasets.providers import make_provider
from deel.datasets.providers import Provider
from deel.datasets.providers.exceptions import DatasetNotFoundError
from deel.datasets.providers.exceptions import InvalidConfigurationError
from deel.datasets.providers.exceptions import VersionNotFoundError
from deel.datasets.providers.ftp_providers import FtpProvider
from deel.datasets.providers.http_providers import HttpSingleFileProvider
from deel.datasets.providers.local_provider import LocalProvider
from deel.datasets.providers.webdav_provider import WebDavProvider
from deel.datasets.providers.webdav_provider import WebDavSimpleAuthenticator

LOCAL_PATH = pathlib.Path(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/",
    )
)


def test_get_version():
    """
    Test the get_version  method.
    """

    # Fake provider class:
    class NoProvider(Provider):
        def list_datasets(self) -> typing.List[str]:
            return []

        def list_versions(self, dataset: str) -> typing.List[str]:
            return []

        def get_folder(
            self,
            name: str,
            version: str = "latest",
            force_update: bool = False,
            returns_version: bool = False,
        ) -> typing.Union[pathlib.Path, typing.Tuple[pathlib.Path, str]]:
            raise DatasetNotFoundError("")

    # Fake provider:
    provider = NoProvider()

    # Check latest:
    assert provider.get_version("latest", ["1.0.2", "1.0.3", "2.0.4"]) == "2.0.4"
    assert provider.get_version("latest", ["2.0.2", "2.0.3", "2.0.4"]) == "2.0.4"
    assert provider.get_version("latest", ["1.0.2", "2.8.3", "3.0.0"]) == "3.0.0"

    # Check exact match:
    assert provider.get_version("1.0.3", ["1.0.2", "1.0.3", "2.0.4"]) == "1.0.3"
    assert provider.get_version("2.0.3", ["2.0.2", "2.0.3", "2.0.4"]) == "2.0.3"
    assert provider.get_version("2.8.3", ["1.0.2", "2.8.3", "3.0.0"]) == "2.8.3"

    # Check wild card match / incomplete:
    assert provider.get_version("1.0", ["1.0.2", "1.0.3", "2.0.4"]) == "1.0.3"
    assert provider.get_version("2.0.*", ["2.0.2", "2.0.3", "2.0.4"]) == "2.0.4"
    assert provider.get_version("3", ["1.0.2", "2.8.3", "3.0.0", "3.0.1"]) == "3.0.1"
    assert provider.get_version("*.0.3", ["1.0.3", "2.0.3", "3.0.3"]) == "3.0.3"
    assert provider.get_version("2.*", ["2.0.2", "2.0.3", "2.0.4"]) == "2.0.4"
    assert provider.get_version("*", ["1.0.2", "2.8.3", "3.0.0", "3.0.1"]) == "3.0.1"

    # Missing version:
    with pytest.raises(VersionNotFoundError):
        provider.get_version("latest", [])
    with pytest.raises(VersionNotFoundError):
        provider.get_version("*", [])
    with pytest.raises(VersionNotFoundError):
        provider.get_version("3.1.*", ["1.0.2", "1.4.5", "2.3.5"])
    with pytest.raises(VersionNotFoundError):
        provider.get_version("2.4.*", ["1.0.2", "1.4.5", "2.3.5"])
    with pytest.raises(VersionNotFoundError):
        provider.get_version("3.*", ["1.0.2", "1.4.5", "2.3.5"])


def test_local_provider():
    """
    Test the local provider factory.
    """

    # Local provider:
    provider = make_provider("local", LOCAL_PATH)

    assert isinstance(provider, LocalProvider)
    assert provider._root_folder == LOCAL_PATH

    assert set(provider.list_datasets()) == set(["dataset1", "dataset2", "dataset3"])
    assert set(provider.list_versions("dataset1")) == set(["0.0.1", "0.1.0", "1.0.0"])
    assert set(provider.list_versions("dataset2")) == set(["1.0.0", "1.0.1"])


def test_webdav_provider():
    """
    Test the webdav provider factory. TBC
    """

    # Local provider:
    provider = make_provider("local", LOCAL_PATH)

    assert isinstance(provider, LocalProvider)
    assert provider._root_folder == LOCAL_PATH

    assert set(provider.list_datasets()) == set(["dataset1", "dataset2", "dataset3"])
    assert set(provider.list_versions("dataset1")) == set(["0.0.1", "0.1.0", "1.0.0"])
    assert set(provider.list_versions("dataset2")) == set(["1.0.0", "1.0.1"])

    # WebDAV provider without authentication:
    provider = make_provider("webdav", LOCAL_PATH, {"url": "https://webdav"})
    assert isinstance(provider, WebDavProvider)
    assert provider._root_folder == LOCAL_PATH
    assert provider._remote_url == "https://webdav"
    assert provider._authenticator is None

    # WebDAV provider with authentication:
    provider = make_provider(
        "webdav",
        LOCAL_PATH,
        {
            "url": "https://webdav",
            "auth": {"method": "simple", "username": "user", "password": "pass"},
        },
    )
    assert isinstance(provider, WebDavProvider)
    assert provider._root_folder == LOCAL_PATH
    assert provider._remote_url == "https://webdav"
    assert isinstance(provider._authenticator, WebDavSimpleAuthenticator)
    assert provider._authenticator.username == "user"
    assert provider._authenticator.password == "pass"

    # WebDAV provider with bad authentication method:
    with pytest.raises(InvalidConfigurationError):
        make_provider(
            "webdav",
            LOCAL_PATH,
            {"url": "https://webdav", "auth": {"method": "token", "token": "abcdef"}},
        )


def test_ftp_provider(ftpserver):
    """
    Test the ftp provider factory.
    """

    # Ftp provider with authentication:
    # First put on the ftp server two files for test
    # using default login/ passwd
    ftpserver.reset_tmp_dirs()
    login_dict = ftpserver.get_login_data()
    ftp = ftplib.FTP()
    ftp.connect(login_dict["host"], login_dict["port"])
    ftp.login(login_dict["user"], login_dict["passwd"])
    ftp.cwd("/")
    ftpserver.put_files(
        {
            "src": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/dataset1/0.0.1/provider_test_data.tar.xz",
            ),
            "dest": "dataset1/0.0.1/provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftpserver.put_files(
        {
            "src": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/dataset1/0.0.1/provider_test_data.tar.xz",
            ),
            "dest": "dataset1/0.0.2/provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftpserver.put_files(
        {
            "src": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/dataset1/0.0.1/provider_test_data.tar.xz",
            ),
            "dest": "dataset2/0.0.2/provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftp.quit()

    ftplib.FTP_PORT = login_dict["port"]
    provider = make_provider(
        "ftp",
        LOCAL_PATH,
        {
            "url": "ftp://localhost/",
            "auth": {
                "method": "simple",
                "username": "fakeusername",
                "password": "qweqwe",
            },
            "port": login_dict["port"],
        },
    )
    assert isinstance(provider, FtpProvider)
    assert provider._root_folder == LOCAL_PATH
    assert provider.list_datasets() == ["dataset1", "dataset2"]
    assert provider.list_versions("dataset1") == ["0.0.1", "0.0.2"]
    assert provider.list_versions("dataset2") == ["0.0.2"]

    # Ftp provider with bad authentication method:
    with pytest.raises(InvalidConfigurationError):
        make_provider(
            "ftp",
            LOCAL_PATH,
            {
                "url": "ftp://ftp.softronics.ch/",
                "auth": {"method": "token", "token": "abcdef"},
            },
        )


def test_http_provider():
    """
    Test the http provider factory.
    """

    single_http_provider = HttpSingleFileProvider(
        LOCAL_PATH, "http://madm.dfki.de/files/sentinel/EuroSAT.zip", "eurosat"
    )

    assert len(single_http_provider.list_datasets()) > 0
    assert len(single_http_provider.list_versions("eurosat")) > 0

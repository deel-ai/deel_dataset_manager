# -*- encoding: utf-8 -*-

import pathlib
import pytest
import typing
import os
import ftplib

from deel.datasets.providers import make_provider, Provider

from deel.datasets.providers.exceptions import (
    DatasetNotFoundError,
    VersionNotFoundError,
)

from deel.datasets.providers.local_provider import LocalProvider
from deel.datasets.providers.webdav_provider import (
    WebDavSimpleAuthenticator,
    WebDavProvider,
)

from deel.datasets.providers.ftp_providers import (
    FtpProvider,
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


def test_factory(ftpserver, tmpdir):
    """
    Test the provider factory.
    """

    # path = pathlib.Path("/data/datasetes")
    path = pathlib.Path(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data/",
        )
    )
    print("Local path {}".format(path))
    # Local provider:
    provider = make_provider("local", path)

    assert isinstance(provider, LocalProvider)
    assert provider._root_folder == path
    print("provider.list_datasets {}".format(provider.list_datasets()))
    assert provider.list_datasets() == ["dataset2", "dataset1"]
    assert provider.list_versions("dataset1") == ["0.0.1", "0.1.0", "1.0.0"]
    assert provider.list_versions("dataset2") == ["1.0.0", "1.0.1"]

    # WebDAV provider without authentication:
    provider = make_provider("webdav", path, {"url": "https://webdav"})
    assert isinstance(provider, WebDavProvider)
    assert provider._root_folder == path
    assert provider._remote_url == "https://webdav"
    assert provider._authenticator is None

    # WebDAV provider with authentication:
    provider = make_provider(
        "webdav",
        path,
        {
            "url": "https://webdav",
            "auth": {"method": "simple", "username": "user", "password": "pass"},
        },
    )
    assert isinstance(provider, WebDavProvider)
    assert provider._root_folder == path
    assert provider._remote_url == "https://webdav"
    assert isinstance(provider._authenticator, WebDavSimpleAuthenticator)
    assert provider._authenticator.username == "user"
    assert provider._authenticator.password == "pass"

    # WebDAV provider with bad authentication method:
    with pytest.raises(ValueError):
        make_provider(
            "webdav",
            path,
            {"url": "https://webdav", "auth": {"method": "token", "token": "abcdef"}},
        )

    # Incorrect provider type:
    with pytest.raises(ValueError):
        make_provider("aws", path)

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
                "data/dataset1/0.0.1/ftp_provider_test_data.tar.xz",
            ),
            "dest": "dataset1/0.0.1/ftp_provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftpserver.put_files(
        {
            "src": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/dataset1/0.0.1/ftp_provider_test_data.tar.xz",
            ),
            "dest": "dataset1/0.0.2/ftp_provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftpserver.put_files(
        {
            "src": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "data/dataset1/0.0.1/ftp_provider_test_data.tar.xz",
            ),
            "dest": "dataset2/0.0.2/ftp_provider_test_data.tar.xz",
        },
        style="rel_path",
        anon=False,
    )
    ftp.quit()

    ftplib.FTP_PORT = login_dict["port"]
    provider = make_provider(
        "ftp",
        path,
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
    assert provider._root_folder == path
    assert provider.list_datasets() == ["dataset1", "dataset2"]
    assert provider.list_versions("dataset1") == ["0.0.1", "0.0.2"]
    assert provider.list_versions("dataset2") == ["0.0.2"]

    # Ftp provider with bad authentication method:
    with pytest.raises(ValueError):
        make_provider(
            "ftp",
            path,
            {
                "url": "ftp://ftp.softronics.ch/",
                "auth": {"method": "token", "token": "abcdef"},
            },
        )

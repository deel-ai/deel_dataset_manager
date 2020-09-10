# -*- encoding: utf-8 -*-

import pathlib
import pytest
import typing

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


def test_factory():
    """
    Test the provider factory.
    """

    path = pathlib.Path("/data/datasetes")

    # Local provider:
    provider = make_provider("local", path)

    assert isinstance(provider, LocalProvider)
    assert provider._root_folder == path

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

    # Ftp provider without authentication:
    print("Ftp provider without authentication ...")
    provider = make_provider(
        "ftp", path, {"url": "ftp://ftp.softronics.ch/mvtec_anomaly_detection/"}
    )
    assert isinstance(provider, FtpProvider)
    assert provider._root_folder == path
    assert provider._remote_url == "ftp://ftp.softronics.ch/mvtec_anomaly_detection/"
    # assert provider.authenticator is None

    # Ftp provider with authentication:
    print("Ftp provider with authentication ...")
    provider = make_provider(
        "ftp",
        path,
        {
            "url": "ftp://ftp.softronics.ch/mvtec_anomaly_detection/",
            "auth": {"method": "simple", "username": "guest", "password": "GU.205dldo"},
        },
    )
    assert isinstance(provider, FtpProvider)
    assert provider._root_folder == path
    assert provider._remote_url == "ftp://ftp.softronics.ch/mvtec_anomaly_detection/"
    assert len(provider.list_datasets()) > 1
    if len(provider.list_versions(dataset="mvtec_anomaly_detection.tar.xz")) > 0:
        assert (
            provider.list_versions(dataset="mvtec_anomaly_detection.tar.xz")[0]
            == "mvtec_anomaly_detection/mvtec_anomaly_detection.tar.xz"
        )

    # Ftp provider with bad authentication method:
    print("Ftp provider with bad authentication method ...")
    with pytest.raises(ValueError):
        make_provider(
            "ftp",
            path,
            {
                "url": "ftp://ftp.softronics.ch/",
                "auth": {"method": "token", "token": "abcdef"},
            },
        )

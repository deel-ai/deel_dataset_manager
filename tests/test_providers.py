# -*- encoding: utf-8 -*-

import pathlib
import pytest

from deel.datasets.providers import make_provider

from deel.datasets.providers.local_provider import LocalProvider
from deel.datasets.providers.webdav_provider import (
    WebDavSimpleAuthenticator,
    WebDavProvider,
)


def test_factory():
    """ Test the provider factory. """

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

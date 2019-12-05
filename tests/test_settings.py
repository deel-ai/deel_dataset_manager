# -*- encoding: utf-8 -*-

import io

from deel.datasets.settings import Settings


def test_constructor():

    # Default constructor:
    settings = Settings()
    assert settings._version == Settings._version
    assert settings._provider_type == Settings._provider_type
    assert settings._provider_options == Settings._provider_options

    # Constructor without provider:
    yaml = """version: 1"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == Settings._provider_type
    assert settings._provider_options == Settings._provider_options

    # Constructor with local provider:
    yaml = """version: 1

path: "/data/datasets"
provider:
    type: "local"

"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "local"
    assert settings._provider_options == {}

    # Constructor with WebDAV provider:
    yaml = """version: 1

path: "/data/datasets"
provider:
    type: "webdav"

"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "webdav"
    assert settings._provider_options == {}

    yaml = """version: 1

path: "/data/datasets"
provider:
    type: "webdav"
    auth:
        method: "simple"
        username: "user"
        password: "pass"
"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "webdav"
    assert settings._provider_options == {
        "auth": {"method": "simple", "username": "user", "password": "pass"}
    }

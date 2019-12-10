# -*- encoding: utf-8 -*-

import io

from pathlib import Path

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
    assert settings._base == Path.home().joinpath(".deel", "datasets")

    # Constructor with local provider:
    yaml = """version: 1

path: /data/datasets
provider:
    type: local

"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "local"
    assert settings._provider_options == {}
    assert settings._base == Path("/data/datasets")

    # Constructor with WebDAV provider:
    yaml = """version: 1

path: /data/datasets
provider:
    type: webdav

"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "webdav"
    assert settings._provider_options == {}
    assert settings._base == Path("/data/datasets")

    yaml = """version: 1

path: /data/datasets
provider:
    type: webdav
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
    assert settings._base == Path("/data/datasets")


def test_gcloud_settings():

    # Test some of the gclouds

    # We need to override find_gcloud_mount_path() for testing
    # purpose
    import deel.datasets._gcloud_utils as _gcloud_utils

    _gcloud_utils.find_gcloud_mount_path = lambda: Path("/mnt/deel-datasets")

    yaml = """version: 1

provider: gcloud"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path("/mnt/deel-datasets")
    assert settings._provider_options == {}

    yaml = """version: 1

provider: gcloud
path: /vol/deel-datasets"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path("/vol/deel-datasets")
    assert settings._provider_options == {}

    # Return None so default path is used:
    _gcloud_utils.find_gcloud_mount_path = lambda: None

    yaml = """version: 1

provider: gcloud"""
    settings = Settings(io.StringIO(yaml))
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path.home().joinpath(".deel", "datasets")
    assert settings._provider_options == {}

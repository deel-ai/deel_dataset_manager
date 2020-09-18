# -*- encoding: utf-8 -*-

import io
import os
import pytest

from pathlib import Path

from deel.datasets.settings import read_settings, ParseSettingsError


def test_constructor():

    # Constructor without provider:
    yaml = """version: 1"""
    with pytest.raises(ParseSettingsError) as ex:
        settings = read_settings(io.StringIO(yaml))
    assert "Missing provider." in str(ex.value)

    # Constructor with local provider:
    yaml = """version: 1

path: /data/datasets
provider:
    type: local

"""
    settings = read_settings(io.StringIO(yaml))["default"]
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
    settings = read_settings(io.StringIO(yaml))["default"]
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
    settings = read_settings(io.StringIO(yaml))["default"]
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
    settings = read_settings(io.StringIO(yaml))["default"]
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path("/mnt/deel-datasets")
    assert settings._provider_options == {}

    yaml = """version: 1

provider: gcloud
path: /vol/deel-datasets"""
    settings = read_settings(io.StringIO(yaml))["default"]
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path("/vol/deel-datasets")
    assert settings._provider_options == {}

    # Return None so default path is used:
    _gcloud_utils.find_gcloud_mount_path = lambda: None

    yaml = """version: 1

provider: gcloud"""
    settings = read_settings(io.StringIO(yaml))["default"]
    assert settings._version == 1
    assert settings._provider_type == "gcloud"
    assert settings._base == Path.home().joinpath(".deel", "datasets")
    assert settings._provider_options == {}


# Test configuration version 2 : multiple providers
def test_configuration_version_2():
    # configuration with 3 providers and path
    yaml = """version: 2

path: /data/datasets
providers:
    provider_1:
        type: webdav
        auth:
            method: "simple"
            username: "provider_1_user"
            password: "provider_1_pass"

    provider_2:
        type: ftp
        auth:
            method: "simple"
            username: "provider_2_user"
            password: "provider_2_pass"

    provider_3:
        type: http
        auth:
            method: "simple"
            username: "provider_3_user"
            password: "provider_3_pass"

    provider_4:
        type: webdav
        folder: datasets
        auth:
            method: "simple"
            username: "provider_4_user"
            password: "provider_4_pass"
"""
    settings_list = read_settings(io.StringIO(yaml))

    assert len(settings_list) == 4
    assert settings_list["provider_1"]._version == 2
    assert settings_list["provider_1"]._provider_type == "webdav"
    assert settings_list["provider_1"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_1_user",
            "password": "provider_1_pass",
        }
    }
    assert settings_list["provider_1"]._base == Path("/data/datasets")

    assert settings_list["provider_2"]._version == 2
    assert settings_list["provider_2"]._provider_type == "ftp"
    assert settings_list["provider_2"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_2_user",
            "password": "provider_2_pass",
        }
    }
    assert settings_list["provider_2"]._base == Path("/data/datasets")

    assert settings_list["provider_3"]._version == 2
    assert settings_list["provider_3"]._provider_type == "http"
    assert settings_list["provider_3"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_3_user",
            "password": "provider_3_pass",
        }
    }
    assert settings_list["provider_4"]._base == Path("/data/datasets")

    assert settings_list["provider_4"]._version == 2
    assert settings_list["provider_4"]._provider_type == "webdav"
    assert settings_list["provider_4"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_4_user",
            "password": "provider_4_pass",
        },
        "folder": "datasets",
    }
    assert settings_list["provider_3"]._base == Path("/data/datasets")

    #  configuration with 3 providers and no path
    yaml = """version: 2

providers:
    provider_1:
        type: webdav
        auth:
            method: "simple"
            username: "provider_1_user"
            password: "provider_1_pass"

    provider_2:
        type: ftp
        auth:
            method: "simple"
            username: "provider_2_user"
            password: "provider_2_pass"
"""
    settings_list = read_settings(io.StringIO(yaml))

    assert len(settings_list) == 2
    assert settings_list["provider_1"]._version == 2
    assert settings_list["provider_1"]._provider_type == "webdav"
    assert settings_list["provider_1"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_1_user",
            "password": "provider_1_pass",
        }
    }
    assert settings_list["provider_1"]._base == Path.home().joinpath(
        ".deel", "datasets"
    )

    assert settings_list["provider_2"]._base == Path(
        os.path.join(Path.home(), ".deel/datasets")
    )
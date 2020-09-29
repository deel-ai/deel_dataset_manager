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
    settings = read_settings(io.StringIO(yaml), "default")
    default_provider = settings.get_provider_list()["default"]
    assert settings._version == 1
    assert default_provider._provider_type == "local"
    assert default_provider._provider_options == {}
    assert settings._base == Path("/data/datasets")

    # Constructor with WebDAV provider:
    yaml = """version: 1

path: /data/datasets
provider:
    type: webdav

"""
    settings = read_settings(io.StringIO(yaml), "default")
    default_provider = settings.get_provider_list()["default"]
    assert settings._version == 1
    assert default_provider._provider_type == "webdav"
    assert default_provider._provider_options == {}
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
    settings = read_settings(io.StringIO(yaml), "default")
    default_provider = settings.get_provider_list()["default"]
    assert settings._version == 1
    assert default_provider._provider_type == "webdav"
    assert default_provider._provider_options == {
        "auth": {"method": "simple", "username": "user", "password": "pass"}
    }
    assert settings._base == Path("/data/datasets")


def test_gcloud_settings():

    # Test some of the gclouds

    # We need to override find_gcloud_mount_path() for testing
    # purpose
    from deel.datasets.providers.gcloud_provider import GCloudProvider
    from deel.datasets.providers.exceptions import InvalidConfigurationError

    GCloudProvider._find_gcloud_mount_path = lambda s, d: "/mnt/{}".format(d)

    yaml = """version: 1

provider:
    type: gcloud
    disk: deel-datasets"""
    settings = read_settings(io.StringIO(yaml), "default")
    default_provider = settings.get_provider_list()["default"]
    assert settings._version == 1
    assert default_provider._provider_type == "gcloud"
    assert default_provider._provider_options == {"disk": "deel-datasets"}

    provider = settings.make_provider()
    assert isinstance(provider, GCloudProvider)
    assert provider.root_folder == Path("/mnt/google-deel-datasets")

    yaml = """version: 1

provider:
    type: gcloud
    disk: deel-datasets
path: /vol/deel-datasets"""
    settings = read_settings(io.StringIO(yaml), "default")
    default_provider = settings.get_provider_list()["default"]
    assert settings._version == 1
    assert default_provider._provider_type == "gcloud"
    assert settings._base == Path("/vol/deel-datasets")
    assert default_provider._provider_options == {"disk": "deel-datasets"}

    provider = settings.make_provider()
    assert isinstance(provider, GCloudProvider)
    assert provider.root_folder == Path("/mnt/google-deel-datasets")

    yaml = """version: 1

provider:
    type: gcloud"""
    try:
        settings = read_settings(io.StringIO(yaml), "default")
        provider = settings.make_provider()
        assert False, "Should raise InvalidConfigurationError."
    except InvalidConfigurationError:
        pass

    # Return None so default path is used:
    def mount_path_raise(s, d):
        raise InvalidConfigurationError()

    GCloudProvider._find_gcloud_mount_path = mount_path_raise
    yaml = """version: 1

provider:
    type: gcloud
    disk: deel-datasets
path: /vol/deel-datasets"""
    try:
        settings = read_settings(io.StringIO(yaml), "default")
        default_provider = settings.get_provider_list()["default"]
        provider = settings.make_provider()
        assert False, "Should raise InvalidConfigurationError."
    except InvalidConfigurationError:
        pass


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
    settings = read_settings(io.StringIO(yaml))
    assert settings._version == 2
    assert settings._base == Path("/data/datasets")
    provider_list = settings.get_provider_list()
    assert len(provider_list) == 4

    assert provider_list["provider_1"]._provider_type == "webdav"
    assert provider_list["provider_1"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_1_user",
            "password": "provider_1_pass",
        }
    }
    assert provider_list["provider_2"]._provider_type == "ftp"
    assert provider_list["provider_2"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_2_user",
            "password": "provider_2_pass",
        }
    }

    assert provider_list["provider_3"]._provider_type == "http"
    assert provider_list["provider_3"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_3_user",
            "password": "provider_3_pass",
        }
    }

    assert provider_list["provider_4"]._provider_type == "webdav"
    assert provider_list["provider_4"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_4_user",
            "password": "provider_4_pass",
        },
        "folder": "datasets",
    }

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
    settings = read_settings(io.StringIO(yaml))
    assert settings._version == 2
    assert settings._base == Path.home().joinpath(".deel", "datasets")
    provider_list = settings.get_provider_list()
    assert len(provider_list) == 2

    assert provider_list["provider_1"]._provider_type == "webdav"
    assert provider_list["provider_1"]._provider_options == {
        "auth": {
            "method": "simple",
            "username": "provider_1_user",
            "password": "provider_1_pass",
        }
    }

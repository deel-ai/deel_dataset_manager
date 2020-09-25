# -*- encoding: utf-8 -*-

import collections
import os
import yaml

from pathlib import Path
from typing import Any, Dict, TextIO

from . import logger
from .providers import make_provider, Provider


# Name of the environment variable containing the path to
# the settings:
ENV_DEFAULT_FILE: str = "DEEL_CONFIGURATION_FILE"

# Default location for the settings file:
DEFAULT_FILE_LOCATION: Path = Path(
    os.getenv(ENV_DEFAULT_FILE, Path.home().joinpath(".deel", "config.yml"))
)

# Default datasets storage location:
DEFAULT_DATASETS_PATH = Path.home().joinpath(".deel", "datasets")


class Settings(object):

    """
    The `Settings` class is a read-only class that contains
    settings for the `deel.datasets` package.

    Settings are stored in a YAML format. The default location
    for the settings file is `$HOME/.deel/config.yml`. The
    `DEEL_DATASETS_CONF` environment variable can be used to
    specify the default location of the file.
    """

    # Version of the settings:
    _version: int

    # Type of the provider for the datasets (gcloud / manual / webdav):
    _provider_type: str

    # Options for the provider:
    _provider_options: Dict[str, Any] = {}

    # The root folder containing the datasets:
    _base: Path

    def __init__(
        self,
        version: int,
        provider_type: str,
        provider_options: Dict[str, Any],
        path: Path,
    ):
        """
        Args:
            version: Version of the settings.
            provider_type: Type of the provider.
            provider_options: Options for the provider.
            path: Local storage path for the datasets.
        """
        self._version = version
        self._provider_type = provider_type
        self._provider_options = provider_options
        self._base = path

    def make_provider(self) -> Provider:
        """
        Creates and returns the provider corresponding to these settings.

        Returns:
            A new `Provider` created from these settings.
        """
        # print("make_provider Settings {}".format(self))
        return make_provider(self._provider_type, self._base, self._provider_options)

    @property
    def local_storage(self) -> Path:
        """
        Returns: The path to the local storage for the datasets.
        """
        return self._base

    def __repr__(self) -> str:
        """
        Output a basic representation of these settings.

        Returns:
            A basic representation of these settings.
        """
        return "{}(version={}, provider_type={}, provider_options={}, base={})".format(
            self.__class__.__name__,
            self._version,
            self._provider_type,
            self._provider_options,
            self._base,
        )


class ParseSettingsError(Exception):
    """
    Exception raised if an issue occurs while parsing the settings.
    """

    pass


def read_one_settings(data: Dict[str, Any], version: int) -> Settings:
    """
    Load `Settings` from the given dictionnary (YAML stream).

    Args:
        data: YAML file settings element dictionnary.

    Returns:
        A `Settings` object constructed from the given data.

    Raises:
        yaml.YAMLError: If the given stream does not contain valid YAML.
        ParseSettingsError: If the given YAML is not valid for settings.
    """

    # Retrieve the provider:
    if "provider" not in data:
        raise ParseSettingsError("Missing provider.")

    if isinstance(data["provider"], dict):
        provider_type = data["provider"]["type"]
        provider_options = data["provider"]
        del provider_options["type"]
    else:
        provider_type = data["provider"]
        provider_options = {}

    # Retrieve the base folder:
    if "path" in data:
        path = Path(data["path"])
    else:
        path = DEFAULT_DATASETS_PATH

    return Settings(version, provider_type, provider_options, path)


def read_settings(stream: TextIO) -> Dict[str, Settings]:
    """
    Load `Settings` from the given YAML stream.

    Args:
        stream: File-like object containing the configuration.

    Returns:
        A `Settings` object constructed from the given YAML stream.

    Raises:
        yaml.YAMLError: If the given stream does not contain valid YAML.
        ParseSettingsError: If the given YAML is not valid for settings.
    """

    settings_list: Dict[str, Settings] = {}
    # We let the error propagate to distinguish between error in
    # parsing YAML and error in constructing settings:
    data = yaml.safe_load(stream)

    # Retrieve the version:
    if "version" not in data:
        raise ParseSettingsError("Missing version.")
    version = int(data["version"])

    if version == 1:
        # Retrieve the provider:
        settings_list.update({"default": read_one_settings(data, version)})
    else:
        # Retrieve the providers:
        if "providers" not in data:
            raise ParseSettingsError("Missing providers list.")

        if isinstance(data["providers"], dict):

            for prov, conf in data["providers"].items():
                d = {"provider": conf}
                if "path" in data:
                    d.update({"path": data["path"]})
                settings_list.update({prov: read_one_settings(d, version)})
        else:
            raise ParseSettingsError("Providers not a dictionary")
    return settings_list


def write_settings(settings: Settings, stream: TextIO, **kwargs):
    """
    Write the given `Settings` to the given stream as YAML.

    Args:
        settings: Settings to write.
        stream: File-like object where the configuration will be written.
        **kwargs: Extra arguments for the `yaml.safe_dump` method.
    """

    yaml.add_representer(
        collections.OrderedDict,
        lambda self, data: yaml.representer.SafeRepresenter.represent_dict(
            self, data.items()
        ),
    )

    # Build the python object:
    data: collections.OrderedDict = collections.OrderedDict()

    data["version"] = settings._version
    data["provider"] = collections.OrderedDict()
    data["provider"]["type"] = settings._provider_type
    data["provider"].update(settings._provider_options)
    data["path"] = str(settings._base.absolute())

    yaml.dump(data, stream, **kwargs)


def get_default_settings() -> Dict[str, Settings]:
    """
    Retrieve the default settings for the current machine.

    Returns:
        The default settings for the current machine.
    """

    file_location: Path = DEFAULT_FILE_LOCATION

    if not file_location.exists():
        logger.warning(
            "[Deprecated] Missing deel.datasets user settings file. "
            "Create a configuration file at {} or set the {} environment "
            "variable accordingly.".format(DEFAULT_FILE_LOCATION, ENV_DEFAULT_FILE)
        )
        return {"default": get_settings_for_local()}

    with open(file_location, "r") as fp:
        settings = read_settings(fp)

    return settings


def get_settings_for_local() -> Settings:
    """
    Retrieve the local default settings.

    Returns:
        The settings for local.
    """
    return Settings(
        version=1,
        provider_type="local",
        provider_options={},
        path=DEFAULT_DATASETS_PATH,
    )


def get_dataset_settings(dataset: str) -> Settings:
    """
    Retrieve the right settings for the current dataset.

    Returns:
        The settings for the current dataset.
    """
    settings_list = get_default_settings()
    for settings in settings_list.values():
        provider = settings.make_provider()
        if dataset in provider.list_datasets():
            return settings
    return next(iter(settings_list.values()))


if __name__ == "__main__":
    settings = get_default_settings()
    print(settings)
    print(settings["default"].make_provider())

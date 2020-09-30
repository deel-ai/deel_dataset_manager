# -*- encoding: utf-8 -*-

import collections
import os
import yaml

from pathlib import Path
from typing import Any, Dict, TextIO

from . import logger
from .providers import make_provider as make_provider, Provider
from .providers.exceptions import DatasetNotFoundError, InvalidConfigurationError


# Name of the environment variable containing the path to
# the settings:
ENV_DEFAULT_FILE: str = "DEEL_CONFIGURATION_FILE"

# Default location for the settings file:
DEFAULT_FILE_LOCATION: Path = Path(
    os.getenv(ENV_DEFAULT_FILE, Path.home().joinpath(".deel", "config.yml"))
)

# Default datasets storage location:
DEFAULT_DATASETS_PATH = Path.home().joinpath(".deel", "datasets")


class SettingsProvider(object):
    """"""

    # Type of the provider for the datasets (gcloud / manual / webdav):
    _provider_type: str

    # Options for the provider:
    _provider_options: Dict[str, Any] = {}

    def __init__(
        self,
        provider_type: str,
        provider_options: Dict[str, Any],
    ):
        """
        Args:
            provider_type: Type of the provider.
            provider_options: Options for the provider.
        """
        self._provider_type = provider_type
        self._provider_options = provider_options

    def create_provider(self, base: Path) -> Provider:
        """
        Creates and returns the provider corresponding to those configurations.
        Args:
            base: path root directory

        Returns:
            A new `Provider` created from these settings.
        """
        return make_provider(self._provider_type, base, self._provider_options)


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

    # Options for the provider:
    _default_provider_: str

    # Options for the provider:
    _provider_list: Dict[str, SettingsProvider] = {}

    # The root folder containing the datasets:
    _base: Path

    def __init__(
        self,
        version: int,
        provider_list: Dict[str, SettingsProvider],
        path: Path,
        default_provider: str = "",
    ):
        """
        Args:
            version: Version of the settings.
            provider_type: Type of the provider.
            provider_options: Options for the provider.
            path: Local storage path for the datasets.
        """
        self._version = version
        self._provider_list = provider_list
        self._base = path
        self._default_provider_ = default_provider

    def get_best_provider(self, dataset: str) -> SettingsProvider:
        """
        Searchs and returns the best settings provider. If the defauit
        provider is defined in the configuration file, it is returned.
        If not and if the dataset is not None, searchs and returns the 
        first settings provider which contains this dataset.
        If not, returns the local settings provider.
        Args:
            dataset: dataset name
        Returns:
            The provider to use
        """

        s_provider: SettingsProvider = SettingsProvider("local", {})
        if "default" in self._provider_list:
            s_provider = self._provider_list["default"]
        elif dataset:
            for sp in self._provider_list.values():
                try:
                    # check provider...
                    provider = sp.create_provider(self._base)
                    if dataset in provider.list_datasets():
                        s_provider = sp
                        break
                except (DatasetNotFoundError, InvalidConfigurationError):
                    pass
        return s_provider

    def make_provider(self, dataset: str = "") -> Provider:
        """
        Creates and returns the provider corresponding to these settings.
        Args:
            dataset: dataset name
        Returns:
            A new `Provider` created from these settings.
        """

        if (
            self._default_provider_ is not None
            and self._default_provider_ in self._provider_list
        ):
            s_provider = self._provider_list[self._default_provider_]
        else:
            s_provider = self.get_best_provider(dataset)

        return s_provider.create_provider(self._base)

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
        return "{}(version={}, base={})".format(
            self.__class__.__name__,
            self._version,
            self._base,
        )

    def get_provider_list(self) -> Dict[str, SettingsProvider]:
        return self._provider_list


class ParseSettingsError(Exception):
    """
    Exception raised if an issue occurs while parsing the settings.
    """

    pass


def read_one_provider(data: Dict[str, Any], version: int) -> SettingsProvider:
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

    return SettingsProvider(provider_type, provider_options)


def read_settings(stream: TextIO, default_provider: str = "") -> Settings:
    """
    Load `Settings` from the given YAML stream.

    Args:
        stream: File-like object containing the configuration.
        default_provider: default provider to use
    Returns:
        A `Settings` object constructed from the given YAML stream.

    Raises:
        yaml.YAMLError: If the given stream does not contain valid YAML.
        ParseSettingsError: If the given YAML is not valid for settings.
    """

    provider_list: Dict[str, SettingsProvider] = {}
    # We let the error propagate to distinguish between error in
    # parsing YAML and error in constructing settings:
    data = yaml.safe_load(stream)

    # Retrieve the version:
    if "version" not in data:
        raise ParseSettingsError("Missing version.")
    version = int(data["version"])

    if version == 1:
        # Retrieve the provider:
        provider_list.update({"default": read_one_provider(data, version)})
    else:
        # Retrieve the providers:
        if "providers" not in data:
            raise ParseSettingsError("Missing providers list.")

        if isinstance(data["providers"], dict):
            for prov, conf in data["providers"].items():
                d = {"provider": conf}
                provider_list.update({prov: read_one_provider(d, version)})
        else:
            raise ParseSettingsError("Providers not a dictionary")

    # Default path is $HOME/.deel/datasets
    path = DEFAULT_DATASETS_PATH

    # Retrieve the base folder:
    if "path" in data:
        path = Path(data["path"])

    return Settings(
        version,
        provider_list,
        path,
        default_provider=default_provider,
    )


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

    if settings._version == 1:
        data["provider"] = collections.OrderedDict()
        s_provider = next(iter(settings.get_provider_list().values()))
        data["provider"]["type"] = s_provider._provider_type
        data["provider"].update(s_provider._provider_type)
        data["path"] = str(settings._base.absolute())
    else:
        data["providers"] = collections.OrderedDict()
        for name, s_provider in settings.get_provider_list().items():
            data["providers"][name] = collections.OrderedDict()
            data["providers"][name]["type"] = s_provider._provider_type
            data["providers"][name]["provider"] = collections.OrderedDict()
            data["providers"][name]["provider"].update(s_provider._provider_options)

    data["path"] = str(settings._base.absolute())

    yaml.dump(data, stream, **kwargs)


def get_default_settings() -> Settings:
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
        return get_settings_for_local()

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
        provider_list={"local": SettingsProvider("local", {})},
        path=DEFAULT_DATASETS_PATH,
    )


if __name__ == "__main__":
    settings = get_default_settings()
    print(settings)
    print(settings.get_provider_list()["default"].create_provider(settings._base))

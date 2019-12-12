# -*- encoding: utf-8 -*-

import os
import typing
import yaml

from pathlib import Path

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


class ParseSettingsError(Exception):
    """ Exception raised if an issue occurs while parsing the settings. """

    pass


class Settings(object):

    """ The `settings` class is a read-only class that contains
    settings for the `deel.datasets` package.

    Settings are stored in a YAML format. The default location
    for the settings file is `$HOME/.deel/config.yml`. The
    `DEEL_DATASETS_CONF` environment variable can be used to
    specify the default location of the file. """

    # Version of the settings:
    _version: int = 0

    # Type of the provider for the datasets (gcloud / manual / webdav):
    _provider_type: str = "webdav"

    # Options for the provider:
    _provider_options: typing.Dict[str, typing.Any] = {
        # Authentication method (if any):
        "auth": {
            "method": "simple",
            "username": "deel-datasets",
            "password": "e]{qE/Pc65z'Nt?zLe-cK!_y?6f6",
        },
        # URL for the provider (if any):
        "url": "https://datasets.deel.ai",
    }

    # The root folder containing the datasets:
    _base: Path = DEFAULT_DATASETS_PATH

    def __init__(self, io: typing.Optional[typing.TextIO] = None):
        """
        Args:
            io: File-like object containing the configuration. If `None`,
            created a default configuration.

        Raises:
            yaml.YAMLError: If the given stream does not contain valid YAML.
            ParseSettingsError: If the given YAML is not valid for settings.
        """

        if io is None:
            return

        # We let the error propagate to distinguish between error in
        # parsing YAML and error in constructing settings:
        data = yaml.safe_load(io)

        # Retrieve the version:
        if "version" not in data:
            raise ParseSettingsError("Missing version.")
        self._version = int(data["version"])

        # Retrieve the provider:
        if "provider" in data:
            if isinstance(data["provider"], dict):
                self._provider_type = data["provider"]["type"]
                self._provider_options = data["provider"]
                del self._provider_options["type"]
            else:
                self._provider_type = data["provider"]
                self._provider_options = {}

        # Retrieve the base folder:
        if "path" in data:
            self._base = Path(data["path"])
        else:
            self._base = self._get_default_path(self._provider_type)

    def _get_default_path(self, provider_type: str) -> Path:
        """ Retrieve the default dataset root path for the given provider type.

        Args:
            provider_type: The type of provider to retrieve the path for.

        Returns:
            The default path for the given provider.
        """

        # Default path is $HOME/.deel/datasets
        path = DEFAULT_DATASETS_PATH

        # For GCloud, we try to find the mount point:
        if provider_type == "gcloud":
            from ._gcloud_utils import find_gcloud_mount_path

            gcloud_path = find_gcloud_mount_path()
            if gcloud_path is not None:
                path = gcloud_path

        return path

    def make_provider(self) -> Provider:
        """ Creates and returns the provider corresponding to these settings.

        Returns:
            A new `Provider` created from these settings.
        """
        return make_provider(self._provider_type, self._base, self._provider_options)

    def __repr__(self) -> str:
        """ Output a basic representation of these settings.

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


def get_default_settings() -> Settings:
    """ Retrieve the default settings for the current machine.

    Returns:
        The default settings for the current machine.
    """

    settings: Settings = Settings()

    if DEFAULT_FILE_LOCATION.exists():
        try:
            with open(DEFAULT_FILE_LOCATION, "r") as fp:
                settings = Settings(fp)
        except Exception:
            logger.warning(
                "Failed to load deel.datasets settings from {}.".format(
                    DEFAULT_FILE_LOCATION
                )
            )
    else:
        logger.warning(
            (
                "[Deprecated] Missing deel.datasets settings file. "
                "Create a configuration file at {} or set the {} environment "
                "variable accordingly."
            ).format(DEFAULT_FILE_LOCATION, ENV_DEFAULT_FILE)
        )

    return settings


if __name__ == "__main__":
    settings = get_default_settings()
    print(settings)
    print(settings.make_provider())

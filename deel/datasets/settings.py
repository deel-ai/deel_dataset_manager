# -*- encoding: utf-8 -*-

import logging
import os
import typing
import yaml

from pathlib import Path

from .providers import make_provider, Provider

# Logger for settings:
logger = logging.getLogger(__name__)

# Name of the environment variable containing the path to
# the settings:
ENV_DEFAULT_FILE: str = "DEEL_CONFIGURATION_FILE"

# Default location for the settings file:
DEFAULT_FILE_LOCATION: Path = Path(
    os.getenv(ENV_DEFAULT_FILE, os.path.join(Path.home(), ".deel", "config.yml"))
)


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
    _base: Path = Path.home().joinpath(".deel", "datasets")

    def __init__(self, io: typing.Optional[typing.TextIO] = None):
        """
        Args:
            io: File-like object containing the configuration. If `None`,
            created a default configuration.
        """

        if io is None:
            return

        data = yaml.safe_load(io)

        # Retrieve the version:
        self._version = int(data["version"])

        # Retrieve the provider:
        if "provider" in data:
            self._provider_type = data["provider"]["type"]
            self._provider_options = data["provider"]
            del self._provider_options["type"]

        # Retrieve the base folder:
        if "path" in data:
            self._base = data["path"]

    def make_provider(self) -> Provider:
        """ Creates and returns the provider corresponding to these settings.

        Returns:
            A new `Provider` created from these settings.
        """
        return make_provider(self._provider_type, self._base, self._provider_options)


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

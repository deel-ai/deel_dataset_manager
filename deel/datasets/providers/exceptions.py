# -*- encoding: utf-8 -*-

import typing


class DatasetNotFoundError(Exception):

    """ Exception thrown by providers when the requested dataset
    is not found. """

    def __init__(self, name: str):
        """
        Args:
            name: Name of the dataset not found.
        """
        super().__init__("Dataset {} not found.".format(name))


class VersionNotFoundError(Exception):

    """ Exception thrown by providers when the requested version
    is not found. """

    def __init__(self, version: typing.Optional[str] = None):
        """
        Args:
            version: Version of the dataset not found (or a version selector).
        """
        super().__init__("No version matching {} found.".format(version))


class DatasetVersionNotFoundError(DatasetNotFoundError, VersionNotFoundError):

    """ Exception thrown by providers when the requested dataset
    version is not found.

    This exception is meant to be more specific than DatasetNotFoundError. """

    def __init__(self, name: str, version: str):
        """
        Args:
            name: Name of the dataset not found.
            version: Version of the dataset not found.
        """
        Exception.__init__(
            self, "Dataset {} for version {} not found.".format(name, version)
        )

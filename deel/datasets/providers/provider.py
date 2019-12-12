# -*- encoding: utf-8 -*-

import abc
import pathlib
import typing

from .exceptions import VersionNotFoundError


class Provider(abc.ABC):

    """ The `Provider` class is an abstract interface for classes
    that provides access to dataset storages. """

    def list_datasets(self) -> typing.List[str]:
        """ List the available datasets for this provider.

        Returns:
            The list of datasets available for this provider.
        """
        pass

    def list_versions(self, dataset: str) -> typing.List[str]:
        """ List the available versions of the given dataset for this
        provider.

        Returns:
            The list of available versions of the given dataset for this
            provider.

        Raises:
            DatasetNotFoundError: If the given dataset does not exist.
        """
        pass

    def get_version(self, version: str, versions: typing.List[str]) -> str:
        """ Retrieve the version from the list of `versions` that best match
        the given one.

        Args:
            version: Version to retrieve. Can be an exact version, e.g., `"3.1.2"`,
            or a wildcard `"3.1.*"`, or `"latest"`.
            versions: List of versions to retrieve the version from. Versions should
            all be of the form `x.y.z`.

        Returns:
            The version in `versions` that best matches `version`.

        Raises:
            VersionNotFoundError: If the specified version did not match
            any version in `versions`.
        """

        # If the list of version is  not found:
        if not versions:
            raise VersionNotFoundError(version)

        versions = sorted(versions)

        # Special case for "latest":
        if version.lower() == "latest":
            return versions[-1]

        # Split the version:
        p = version.split(".")
        p += ["*"] * (3 - len(p))
        x, y, z = p

        # Best version (x, y, z)
        vu, vy, vz = "", "", ""

        for tversion in versions:

            # Special handler for old "latest":
            if tversion == "latest":
                continue

            cu, cy, cz = tversion.split(".")

            # The version does not match the one we are testing:
            if cu != x and x != "*" or cy != y and y != "*" or cz != z and z != "*":
                continue

            vu, vy, vz = max((cu, cy, cz), (vu, vy, vz))

        if vu == "":
            raise VersionNotFoundError(version)

        return "{}.{}.{}".format(vu, vy, vz)

    def get_folder(
        self, name: str, version: str = "latest", force_update: bool = False
    ) -> pathlib.Path:
        """ Retrieve the root folder for the given dataset.

        Args:
            name: Name of the dataset to retrieve the folder for.
            version: Version of the dataset to retrieve the folder for. Can be
            an exact version like `"3.1.2"`, or `"latest"`, or a wildcard, e.g.,
            `"3.1.*"`.
            force_update: Force the update of the local dataset if possible.
            May have no effect on some providers.

        Returns:
            A path to the root folder for the given dataset name.

        Raises:
            DatasetNotFoundError: If the requested dataset was not found by this
            provider.
            DatasetVersionNotFoundError: If the requested version of the dataset was
            not found by this provider.
        """
        pass

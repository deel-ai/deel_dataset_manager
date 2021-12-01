# -*- coding: utf-8 -*-
# Copyright IRT Antoine de Saint Exupéry et Université Paul Sabatier Toulouse III - All
# rights reserved. DEEL is a research program operated by IVADO, IRT Saint Exupéry,
# CRIAQ and ANITI - https://www.deel.ai/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""The `GCloudProvider` is a simple alias for `LocalProvider`."""
from pathlib import Path

import psutil

from . import logger
from .exceptions import InvalidConfigurationError
from .local_provider import LocalProvider


class GCloudProvider(LocalProvider):
    """The `GCloudProvider` is a simple alias for `LocalProvider`."""

    # Link to the GCloud drive:
    _GCLOUD_DRIVE_BASE_PATH = Path("/dev/disk/by-id/")

    def __init__(self, disk: str):
        super().__init__(self._find_gcloud_mount_path(disk))

    def _find_gcloud_mount_path(self, disk: str) -> Path:
        """
        -Try to find the GCloud datasets mount path.

        Returns:
            The mount path for the specified GCloud drive on the current machine.

        Raises:
            InvalidConfigurationError: If the disk does not exist or is not mounted.
        """
        _GCLOUD_DRIVE_PATH = self._GCLOUD_DRIVE_BASE_PATH.joinpath(disk)
        if not _GCLOUD_DRIVE_PATH.exists():
            raise InvalidConfigurationError(
                "Disk {} not found.".format(_GCLOUD_DRIVE_PATH)
            )

        # Find the actual drive:
        target_drive = _GCLOUD_DRIVE_PATH.resolve()
        logger.info("Disk {} targets {}.".format(_GCLOUD_DRIVE_PATH, target_drive))

        # List the mount points:
        for part in psutil.disk_partitions(True):
            if target_drive == Path(part.device):
                logger.info(
                    "Disk {} mounted to {}.".format(_GCLOUD_DRIVE_PATH, part.mountpoint)
                )
                return Path(part.mountpoint)

        raise InvalidConfigurationError("Disk {} not mounted.".format(target_drive))

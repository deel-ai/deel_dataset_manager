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
import logging
import pathlib
import typing

from .exceptions import InvalidConfigurationError
from .provider import Provider

logger = logging.getLogger(__name__)


def make_provider(
    provider_type: str,
    root_path: pathlib.Path,
    provider_options: typing.Dict[str, typing.Any] = {},
) -> Provider:

    """
    Create a new provider using the given arguments.

    Args:
        provider_type: Type of the provider.
        root_path: Local path for the datasets.
        provider_options: Extra options to pass to the provider
        constructor.

    Returns:
        A provider corresponding to the given arguments.

    Raises:
        ValueError: If the given `provider_type` is invalid or if the
        given options do not match the given provider.
    """

    # Case of a local provider as a real provider:
    # source provided by a network mounted disk for exemple
    if provider_type == "local":
        from .local_as_provider import LocalAsProvider
        from .local_provider import LocalProvider

        if "path" not in provider_options:
            provider_options.update({"path": root_path})
        source_path = provider_options["path"]

        if "copy" in provider_options and provider_options["copy"] is True:
            return LocalAsProvider(root_folder=root_path, source_folder=source_path)

        return LocalProvider(root_folder=source_path)

    elif provider_type == "gcloud":
        from .gcloud_provider import GCloudProvider

        if "disk" not in provider_options:
            raise InvalidConfigurationError("No disk specified for gcloud provider.")

        return GCloudProvider(disk="google-" + provider_options["disk"])

    elif provider_type == "webdav":
        from .webdav_provider import (WebDavAuthenticator, WebDavProvider,
                                      WebDavSimpleAuthenticator)

        # Remote path:
        remote_path = ""
        if "folder" in provider_options:
            remote_path = provider_options["folder"]

        # If authentication is required:
        webdav_authenticator: typing.Optional[WebDavAuthenticator] = None
        if "auth" in provider_options:

            # We currently only support simple authentication:
            if provider_options["auth"]["method"] == "simple":
                webdav_authenticator = WebDavSimpleAuthenticator(
                    provider_options["auth"]["username"],
                    provider_options["auth"]["password"],
                )
            else:
                raise InvalidConfigurationError(
                    "Invalid authentication method '{}' for WebDAV provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return WebDavProvider(
            root_path,
            remote_url=provider_options["url"],
            remote_path=remote_path,
            authenticator=webdav_authenticator,
        )

    elif provider_type == "ftp":
        from .ftp_providers import FtpProvider, FtpSimpleAuthenticator

        # If authentication is required:
        ftp_authenticator: typing.Optional[FtpSimpleAuthenticator] = None
        if "auth" in provider_options:

            # We currently only support simple authentication:
            if provider_options["auth"]["method"] == "simple":
                ftp_authenticator = FtpSimpleAuthenticator(
                    provider_options["auth"]["username"],
                    provider_options["auth"]["password"],
                )
            else:
                raise InvalidConfigurationError(
                    "Invalid authentication method '{}' for FTP provider.".format(
                        provider_options["auth"]["method"]
                    )
                )

        return FtpProvider(
            root_path,
            remote_url=provider_options["url"],
            authenticator=ftp_authenticator,
        )

    raise InvalidConfigurationError("Invalid provider type '{}'.".format(provider_type))

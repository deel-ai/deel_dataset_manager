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
import typing


class ProviderNotAvailableError(Exception):
    """
    Exception raised if the provider is not available.
    """

    pass


class InvalidConfigurationError(Exception):
    """
    Exception raised if the provider configuration is invalid.
    """

    pass


class DatasetNotFoundError(Exception):

    """
    Exception thrown by providers when the requested dataset
    is not found.
    """

    def __init__(self, name: str):
        """
        Args:
            name: Name of the dataset not found.
        """
        super().__init__("Dataset {} not found.".format(name))


class VersionNotFoundError(Exception):

    """
    Exception thrown by providers when the requested version
    is not found.
    """

    def __init__(self, version: typing.Optional[str] = None):
        """
        Args:
            version: Version of the dataset not found (or a version selector).
        """
        super().__init__("No version matching {} found.".format(version))


class DatasetVersionNotFoundError(DatasetNotFoundError, VersionNotFoundError):

    """
    Exception thrown by providers when the requested dataset
    version is not found.

    This exception is meant to be more specific than DatasetNotFoundError.
    """

    def __init__(self, name: str, version: str):
        """
        Args:
            name: Name of the dataset not found.
            version: Version of the dataset not found.
        """
        Exception.__init__(
            self, "Dataset {} for version {} not found.".format(name, version)
        )

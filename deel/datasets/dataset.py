# -*- encoding: utf-8 -*-

import pathlib
import typing

from .settings import Settings, get_default_settings


class InvalidModeError(Exception):

    """ Exception raised when a mode is not available for a
    given dataset. """

    def __init__(self, dataset: "Dataset", mode: str):
        """
        Args:
            dataset: Dataset for which the mode is not available.
            mode: Mode not available.
        """
        super().__init__(
            "Mode {} not available for dataset {}.".format(mode, dataset.name)
        )


class Dataset(object):

    """
    Dataset is the base class for all DEEL dataset and can be used as
    a non-specific dataset handler.

    A `Dataset` object can be extended to easily interface with the local
    file system to access datasets files using the `load` method.

    A dataset can be loaded using different modes (see `available_modes`
    and `default_mode`). Inheriting classes can add extra modes by providing
    `_load_MODE` method and overriding `_default_mode`.

    Example:
        Basic usage of the `Dataset` class is via the `load` method.

        >>> dataset = Dataset("blink")
        >>> dataset.load()
        PosixPath('/home/username/.deel/datasets/blink/3.0.1')
    """

    # Name and version of the dataset:
    _name: str
    _version: str

    # The settings to use:
    _settings: Settings

    # The default mode:
    _default_mode: str = "path"

    # Indicates if this dataset consists of a single file:
    _single_file: bool = False

    def __init__(
        self,
        name: str,
        version: str = "latest",
        settings: typing.Optional[Settings] = None,
    ):
        """ Creates a new dataset of the given name and version.

        Args:
            name: Name of the dataset.
            version: Version of the dataset.
            settings: The settings to use for this dataset, or `None` to use the
            default settings.
        """
        self._name = name
        self._version = version

        if settings is None:
            self._settings = get_default_settings()
        else:
            self._settings = settings

    @property
    def name(self) -> str:
        """ Returns: The name of the dataset. """
        return self._name

    @property
    def version(self) -> str:
        """ Returns: The requested version of the dataset. """
        return self._version

    @property
    def available_modes(self) -> typing.List[str]:
        """ Retrieve the list of available modes for this dataset.

        Returns:
            The list of available modes for this dataset.
        """
        # We lookup all attributes of the class starting with load_,
        # and we discard the ones that are not callable (even if there
        # should not be any most of the time):
        return [
            fn.lstrip("load_")
            for fn in dir(self)
            if fn.startswith("load_") and callable(getattr(self, fn))
        ]

    @property
    def default_mode(self) -> str:
        """ Retrieve the default mode for this dataset.

        Returns:
            The default mode for this dataset.
        """
        return self._default_mode

    def load_path(self, path: pathlib.Path) -> pathlib.Path:
        """ Load method for path mode.

        Args:
            path: Path of the dataset.

        Returns:
            The actual path to the dataset.
        """
        return path

    def load(
        self, mode: typing.Optional[str] = None, force_update: bool = False, **kargs
    ) -> typing.Any:
        """ Load this dataset as specified by `mode`.

        This method checks that the given `mode` is valid, retrieve the dataset
        files using a `Provider` and then dispatches the actual loading of the
        data to a `_load_MODE` method.

        If this dataset consists of a single file as specified by `_single_file`,
        the path used will be the one of this file, otherwize, the folder will
        be used.

        Args:
            mode: Mode to load the dataset, or `None` to use the default mode.
            force_update: Force update of the dataset if possible.
            **kargs: Extra arguments for the specific mode.

        Returns:
            The dataset as specified by `mode` and the given extra arguments.

        Raises:
            InvalidModeError: If the given mode is not available for this dataset.
        """

        if mode is None:
            mode = self.default_mode

        if mode not in self.available_modes:
            raise InvalidModeError(self, mode)

        path = self._settings.make_provider().get_folder(
            self._name, self._version, force_update=force_update
        )

        # If single file, retrieve the path to the first file:
        if self._single_file:
            path = next(path.iterdir())

        # Retrieve the method:
        load_fn = getattr(self, "load_" + mode)

        return load_fn(path, **kargs)
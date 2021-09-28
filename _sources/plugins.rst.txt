.. _plugins:

Plugins
-------

A DEEL dataset plugin is an extension of the
:py:class:`.Dataset` or
:py:class:`.VolatileDataset` class defined in the DEEL
dataset manager project.
It allows to access to specific datasets files using the load method of defined
modes.

Extending the :py:class:`.Dataset` class
........................................

Below is an example implementation of a dataset class ``ExampleDataset``.
The ``load_XXX`` methods defines the various mode, e.g. ``load_pytorch`` adds
a ``pytorch`` mode to the dataset.
The default mode used (when none is specified) can be set using the
``_default_mode`` class attribute.

.. code-block:: python

    import h5py
    import pathlib
    import typing

    from deel.datasets.dataset import Dataset
    from deel.datasets.settings import Settings


    class ExampleDataset(Dataset):

        # Default mode:
        _default_mode: str = "numpy"

        def __init__(
            self,
            version: str = "latest",
            settings: typing.Optional[Settings] = None
        ):
            """
            Args:
                version: Version of the dataset.
                settings: The settings to use for this dataset, or `None` to use the
                default settings.
            """
            # `data_name` is the name of the folder containing the dataset on the
            # provider (remote or local).
            super().__init__("data_name", version, settings)

        def load_numpy(self, path: pathlib.Path):
            """
            Numpy mode for this dataset.
            """
            # Dataset-specific code:
            return data

        def load_csv(self, path: pathlib.Path):
            """
            CSV mode for this dataset.
            """

            import pandas as pd

            return pd.read_csv(path, sep=";", index_col=0)

        def load_pytorch(
            self,
            path: pathlib.Path,
            nstack: int = 4,
            transform: typing.Callable = None,
        ):
            """
            Pytorch mode for this dataset. With extra arguments that can
            be passed to the `deel.datasets.load` method using named parameters.
            """
            from .torch import SourceDataSet

            return SourceDataSet(self.load_path(path), nstack, transform)


By default, the ``with_info`` option will return a dictionary containing the name
and the version of the dataset.
If you want to provide extra information, you can return a dictionary from the
``load_XXX`` methods, e.g.:

.. code-block:: python

    def load_pytorch(self, path: pathlib.Path):
        # Load a pytorch dataset:
        dataset = ...

        return dataset, {"classes": ["foo", "bar"}

Utility functions
.................

The ``deel.datasets.utils`` package contains utility functions to load ``numpy``,
``pytorch`` and ``tensorflow`` image dataset in a consistent way, and the ``Dataset``
class contains some utility methods to generate the information dictionary from
the return of these methods.
Here is a very simple example for loading a dataset:

.. code-block:: python

    def load_pytorch(self, path: pathlib.Path, image_size: Tuple[int, int]):
        # Use relative import only if you are inside the deel package:
        from ..utils import load_pytorch_image_dataset

        # Load the dataset using the utility function:
        dataset, idx_to_class = load_pytorch_image_dataset(
            self.load_path(path),  # This is require only if `load_path` modifies the path.
            image_size=image_size,
            train_split=.7,
        )

        # The `_make_class_info` is provided by `Dataset`:
        return dataset, self._make_class_info(idx_to_class)

Packaging the dataset(s)
........................

To be found by the dataset manager, the ``ExampleDataset`` class must be put in
a package with a specific ``entrypoint`` (defined in ``setup.py``).

The entry point provides to the plugin to be discovered and used by DEEL dataset
manager project.
The name of the DEEL dataset manager entry point is unique:
``plugins.deel.dataset``.
It is possible to define many aliases for the same plugin by adding multiple
``alias = package:plugin class`` entries in entry points list.

.. code-block:: python

    # Assuming `ExampleDataset` is in `my_dataset/__init__.py`:
    from setuptools import setup

    setup(
        # Other `setup` arguments:
        ...

        # Entry points:
        entry_points={
            "plugins.deel.dataset": [
                "example = my_dataset:ExampleDataset",
                "my_dataset.example = my_dataset:ExampleDataset"
            ]
        }
    )

A single plugin can expose multiple datasets through different entry points.

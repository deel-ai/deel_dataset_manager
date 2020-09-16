# -*- encoding: utf-8 -*-

import os
import pathlib
import typing

from deel.datasets.utils import (
    load_pytorch_image_dataset,
    load_numpy_image_dataset,
    load_hierarchical_python_image_dataset,
)

path_hierachical = pathlib.Path(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/dataset3/1.0.0/bottle",
    )
)

path = pathlib.Path(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "data/dataset3/1.0.0/bottle/ground_truth",
    )
)


def dispatch_fn(
    path: pathlib.Path,
) -> typing.Optional[typing.Tuple[typing.List[str], str]]:
    """
    Args:
        path: path of the folder containing the images
    Returns a tuple with the name of the dataset
    """
    parts = path.parts

    if parts[1] == "train":
        return ["train"], parts[0]

    elif parts[1] == "test":

        if parts[2] == "good":  # good are without anomaly
            return ["test"], parts[0]
        else:
            return ["unknown"], "{}_{}".format(parts[0], parts[-1])

    else:
        return ["ground_truth"], "{}_{}".format(parts[0], parts[-1])


def test_load_hierarchical_python_image_dataset():
    """
    Test the pytorch image method
    """

    dataset = load_hierarchical_python_image_dataset(
        folder=path_hierachical,
        dispatch_fn=dispatch_fn,
    )

    assert "ground_truth" in dataset
    assert len(dataset["ground_truth"]) == 3


def test_load_pytorch_image_dataset():
    """
    Test the pytorch image method
    """

    dataset, idx_to_class = load_pytorch_image_dataset(
        path,
        image_size=(64, 64),
        train_split=0.8,
    )

    # print(len(dataset))
    assert len(dataset) == 2
    # print(idx_to_class)
    assert idx_to_class == {0: "broken_large", 1: "broken_small", 2: "contamination"}


def test_load_numpy_image_dataset():
    """
    Test the numpy image method
    """

    dataset, idx_to_class = load_numpy_image_dataset(
        path,
        image_size=(64, 64),
        train_split=0.8,
    )

    # print(len(dataset))
    assert len(dataset) == 2
    # print(idx_to_class)
    assert idx_to_class == {0: "broken_large", 1: "broken_small", 2: "contamination"}

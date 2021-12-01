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
# -*- encoding: utf-8 -*-
import os
import pathlib
import typing

from deel.datasets.utils import load_hierarchical_python_image_dataset
from deel.datasets.utils import load_numpy_image_dataset
from deel.datasets.utils import load_pytorch_image_dataset
from deel.datasets.utils import load_tensorflow_image_dataset
from deel.datasets.utils import split_datasets_on_label
from deel.datasets.utils import split_on_label

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

n_images_file = 0
for dir in path.iterdir():
    for f in path.joinpath(dir).glob("*.png"):
        n_images_file += 1

n_train_img = int(n_images_file * 0.8)

n_broken_small_img = 0
for _ in path.joinpath("broken_small").glob("*.png"):
    n_broken_small_img += 1


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

    assert len(dataset[0]) == n_train_img
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
    assert len(dataset[0][0]) == n_train_img
    assert idx_to_class == {0: "broken_large", 1: "broken_small", 2: "contamination"}


def test_numpy_split_on_label():
    """
    Test the numpy split on label methos
    """
    # print("========> test_numpy_split_on_label IN")
    dataset, _ = load_numpy_image_dataset(
        path,
        image_size=(64, 64),
        train_split=0.8,
    )
    (train_in, train_out) = split_on_label(dataset[0], [1])
    (test_in, test_out) = split_on_label(dataset[1], [1])

    assert len(train_in[0]) + len(test_in[0]) == n_broken_small_img
    assert len(train_in[0]) + len(train_out[0]) == len(dataset[0][0])
    assert len(test_in[0]) + len(test_out[0]) == len(dataset[1][0])

    (train_in, train_out), (test_in, test_out) = split_datasets_on_label(dataset, [1])
    assert len(train_in[0]) + len(test_in[0]) == n_broken_small_img
    assert len(train_in[0]) + len(train_out[0]) == len(dataset[0][0])
    assert len(test_in[0]) + len(test_out[0]) == len(dataset[1][0])
    # print("========> test_numpy_split_on_label OUT")


def test_torch_split_on_label():
    """
    Test the torch split on label methos
    """
    # print("========> test_torch_split_on_label IN")
    dataset, _ = load_pytorch_image_dataset(
        path,
        image_size=(64, 64),
        train_split=0.8,
    )
    (train_in, train_out) = split_on_label(dataset[0], [1])
    (test_in, test_out) = split_on_label(dataset[1], [1])

    assert len(train_in) + len(test_in) == n_broken_small_img
    assert len(train_in) + len(train_out) == len(dataset[0])
    assert len(test_in) + len(test_out) == len(dataset[1])

    (train_in, train_out), (test_in, test_out) = split_datasets_on_label(dataset, [1])

    assert len(train_in) + len(test_in) == n_broken_small_img
    assert len(train_in) + len(train_out) == len(dataset[0])
    assert len(test_in) + len(test_out) == len(dataset[1])
    # print("========> test_torch_split_on_label OUT")


def _test_tensorflow_split_on_label():
    """
    Test the tensorflow split on label methos
    """
    # print("========> _test_tensorflow_split_on_label IN")
    dataset, _ = load_tensorflow_image_dataset(
        path,
        image_size=(64, 64),
        train_split=0.8,
    )
    (train_in, train_out) = split_on_label(dataset[0], [1])
    (test_in, test_out) = split_on_label(dataset[1], [1])

    # TBC
    train_in_size = 0
    for _, _ in train_in:
        train_in_size += 1

    train_out_size = 0
    for _, _ in train_out:
        train_out_size += 1

    test_in_size = 0
    for _, _ in test_in:
        test_in_size += 1

    test_out_size = 0
    for _, _ in test_out:
        test_out_size += 1

    assert train_in_size + test_in_size == n_broken_small_img
    assert train_in_size + train_out_size == len(dataset[0])
    assert test_in_size + test_out_size == len(dataset[1])

    (train_in, train_out), (test_in, test_out) = split_datasets_on_label(dataset, [1])
    # TBC
    train_in_size = 0
    for _, _ in train_in:
        train_in_size += 1

    train_out_size = 0
    for _, _ in train_out:
        train_out_size += 1

    test_in_size = 0
    for _, _ in test_in:
        test_in_size += 1

    test_out_size = 0
    for _, _ in test_out:
        test_out_size += 1
    assert train_in_size + test_in_size == n_broken_small_img
    assert train_in_size + train_out_size == len(dataset[0])
    assert test_in_size + test_out_size == len(dataset[1])
    # print("========> test_numpy_split_on_label OUT")


# if __name__ == "__main__":
#     test_numpy_split_on_label()
#     _test_tensorflow_split_on_label()
#     test_torch_split_on_label()

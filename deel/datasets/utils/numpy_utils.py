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
from typing import Sequence
from typing import Tuple

import numpy as np


def numpy_split_on_label(
    dataset: Tuple[np.ndarray, np.ndarray], labels_in: Sequence[int]
) -> Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]:
    """
    Allows to split a numpy dataset in in-dataset and out-dataset according to labels_in
    Args:
        dataset: a numpy dataset
        labels_in: array of 'normal' labels
    Returns:
        a tuple of split datasets (dataset_in, dataset_out),
    """

    if not isinstance(dataset, tuple):
        raise ValueError("Invalid dataset type")

    in_mask = np.isin(dataset[1], labels_in)

    train_in_labels = dataset[1][in_mask]
    train_in_images = dataset[0][in_mask]
    train_out_labels = dataset[1][~in_mask]
    train_out_images = dataset[0][~in_mask]

    return (
        (train_in_images, train_in_labels),
        (train_out_images, train_out_labels),
    )

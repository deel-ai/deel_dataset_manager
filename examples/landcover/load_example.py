# -*- encoding: utf-8 -*-

import deel.datasets as datasets


# Load the dataset:
patches, labels = datasets.load("landcover")
print("Successfully loaded landcover dataset!")
print(
    (
        "  Dataset contains {} samples with patches (shape={}) "
        "and labels (shape={})."
    ).format(len(patches), patches[0].shape, labels[0].shape)
)

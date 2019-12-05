# -*- encoding: utf-8 -*-

import deel.datasets.landcover as landcover


# Load the dataset:
patches, labels = landcover.load()
print("Successfully loaded landcover dataset!")
print(
    (
        "  Dataset contains {} samples with patches (shape={}) "
        "and labels (shape={})."
    ).format(len(patches), patches[0].shape, labels[0].shape)
)

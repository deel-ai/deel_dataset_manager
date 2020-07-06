# -*- encoding: utf-8 -*-

from pathlib import Path
from typing import Optional, Callable, List, Tuple

import torch
import torchvision.transforms

from PIL import Image
from torch.utils.data import Dataset


class SourceDataSet(Dataset):
    """Dataset of source images."""

    def __init__(
        self,
        path: Path,
        num_stack: int = 4,
        transform: Optional[Callable[[Image.Image], Image.Image]] = None,
    ):

        self.num_stack = num_stack

        self.items: List[Tuple[List[Path], Tuple[float, float]]] = []

        for episode in path.iterdir():
            with open(episode.joinpath("annotation.txt"), "r") as fp:
                annotations = [line.split() for line in fp.readlines()]

            for idx, ann in enumerate(annotations):
                indexes = [max(0, i) for i in range(idx - self.num_stack + 1, idx + 1)]
                images = [episode.joinpath(annotations[i][0]) for i in indexes]
                actions = float(ann[1]), float(ann[2])
                self.items.append((images, actions))

        if transform:
            self.transform = torchvision.transforms.Compose(
                [transform, torchvision.transforms.ToTensor()]
            )
        else:
            self.transform = torchvision.transforms.ToTensor()

    def loader(self, path):
        with open(path, "rb") as fp:
            return self.transform(Image.open(fp).convert("RGB"))

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx) -> Tuple[torch.Tensor, Tuple[float, float]]:
        return (
            torch.stack([self.loader(path) for path in self.items[idx][0]]),
            self.items[idx][1],
        )

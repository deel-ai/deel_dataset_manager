# -*- encoding: utf-8 -*-

import typing

import torch
import torchvision.transforms as transforms
from torch import Tensor
from torch import nn
from torch.utils.data import Dataset

# uncomment 2 lines below for local test
# import os, sys
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from deel.datasets import load as load_dataset


class Model:

    # Number of classes:
    _nclasses: int

    # The keras model:
    _model: nn.Sequential

    def __init__(self, num_classes: int):
        """
        Args:
            num_classes: Number of classes.
        """
        self._nclasses = num_classes

        self._model = self.build_model()

        self.optimizer = torch.optim.Adam(self._model.parameters())
        self.loss = torch.nn.CrossEntropyLoss()

    def train(
        self,
        train_set: Dataset,
        validation_set: Dataset,
        batch_size: int = 32,
        nepochs: int = 100,
    ):
        """ Train the model using the given sets and parameters.

        Args:
            train_set: Training set to use.
            validation_set: Validation set to use.
            batch_size: Size of the batch to use.
            nepochs: Number of epochs to train.
        """

        def mean_loss(losses: typing.List[float]):
            if not losses:
                return "N/A"
            return sum(losses) / len(losses)

        print("train : {} valid : {}".format(len(train_set), len(valid_set)))

        loaders = {
            "train": torch.utils.data.DataLoader(train_set, batch_size=batch_size),
            "valid": torch.utils.data.DataLoader(valid_set, batch_size=batch_size),
        }
        for epoch in range(nepochs):
            losses = {k: [] for k in loaders}
            for mode, loader in loaders.items():
                if mode == "train":
                    self._model.train()
                else:
                    self._model.eval()

                for batch in loader:
                    x, y = batch
                    if mode == "train":
                        self.optimizer.zero_grad()
                    yhat = self._model(x)
                    loss = self.loss(yhat, y)
                    losses[mode].append(loss.detach().cpu().tolist())
                    if mode == "train":
                        loss.backward()
                        self.optimizer.step()
            print(
                "Losses epoch {} : {}".format(
                    epoch,
                    " ".join(
                        [
                            "{}: {:.3}".format(mode, mean_loss(val))
                            for mode, val in losses.items()
                        ]
                    ),
                )
            )

    def predict(self, x: Tensor):
        """ Predict the label of the image.

        Args:
            x: the images to predict a label for.

        Returns:
            Prediction for the images (index of the class).
        """
        yhat = self._model(x)
        return torch.argmax(yhat, dim=1)

    def build_model(self) -> nn.Sequential:
        model = []
        num_feats = [3, 32, 32]
        for num_feat_in, num_feat_out in zip(num_feats[:-1], num_feats[1:]):
            model.append(
                nn.Conv2d(num_feat_in, num_feat_out, kernel_size=(3, 3), stride=(1, 1))
            )
            model.append(nn.ReLU())
            model.append(nn.BatchNorm2d(num_features=32))
            model.append(nn.MaxPool2d(kernel_size=(2, 2)))

        model.append(nn.Flatten())

        lin_feats = [6272, 1052, 128, 64]
        for num_feat_in, num_feat_out in zip(lin_feats[:-1], lin_feats[1:]):
            model.append(nn.Dropout(0.5))
            model.append(nn.Linear(num_feat_in, num_feat_out))
            model.append(nn.ReLU())

        model.append(nn.Linear(lin_feats[-1], self._nclasses))
        model.append(nn.Softmax(dim=1))

        return nn.Sequential(*model)


# Images are expected at size 64x64
image_size = (64, 64)
transform = transforms.Compose([transforms.Resize(image_size), transforms.ToTensor()])

# Load dataset splits for PyTorch
train_set, valid_set, test_set = load_dataset(
    "blink", mode="pytorch", percent_train=0.4, percent_val=0.4, transform=transform
)

# list of classes as string from  dataset
label_names = train_set.dataset.classes
print("Classes in dataset : {}".format(label_names))

# build model
model = Model(len(label_names))
# and train it
model.train(train_set, valid_set, batch_size=32, nepochs=1)

# test prediction on one test batch:
test_loader = torch.utils.data.DataLoader(test_set, batch_size=32)
for images, labels in test_loader:  # Only take a single batch
    predictions = model.predict(images)

    # get correct and incorrect predictions
    correct = predictions == labels
    incorrect = predictions != labels

    print(
        "TEST : {} correct predictions and {} incorrect".format(
            sum(correct), sum(incorrect)
        )
    )
    break

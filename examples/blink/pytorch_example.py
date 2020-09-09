# -*- encoding: utf-8 -*-

import typing

import torch
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

    # The device to use:
    _device: torch.device

    def __init__(
        self,
        num_classes: int,
        device: torch.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        ),
    ):
        """
        Args:
            num_classes: Number of classes.
        """
        self._nclasses = num_classes
        self._model = self.build_model().to(device)
        self._device = device

        self.optimizer = torch.optim.Adam(self._model.parameters())
        self.loss = torch.nn.CrossEntropyLoss()

    def train(
        self,
        train_set: Dataset,
        validation_set: Dataset,
        batch_size: int = 32,
        nepochs: int = 100,
    ):
        """Train the model using the given sets and parameters.

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

        print("train: {}, valid: {}".format(len(train_set), len(valid_set)))

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
                    yhat = self._model(x.to(self._device))
                    loss = self.loss(yhat, y.to(self._device))
                    losses[mode].append(loss.detach().cpu().tolist())
                    if mode == "train":
                        loss.backward()
                        self.optimizer.step()
            print(
                "Losses epoch {}: {}".format(
                    epoch,
                    " ".join(
                        [
                            "{}={:.3}".format(mode, mean_loss(val))
                            for mode, val in losses.items()
                        ]
                    ),
                )
            )

    def predict(self, x: Tensor):
        """Predict the label of the image.

        Args:
            x: the images to predict a label for.

        Returns:
            Prediction for the images (index of the class).
        """
        yhat = self._model(x.to(self._device))
        return torch.argmax(yhat, dim=1).cpu()

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

        lin_feats = [6272, 512, 128, 64]
        for num_feat_in, num_feat_out in zip(lin_feats[:-1], lin_feats[1:]):
            model.append(nn.Dropout(0.5))
            model.append(nn.Linear(num_feat_in, num_feat_out))
            model.append(nn.ReLU())

        model.append(nn.Linear(lin_feats[-1], self._nclasses))
        model.append(nn.Softmax(dim=1))

        return nn.Sequential(*model)


# Images are expected at size 64x64
image_size = (64, 64)

# Load dataset splits for PyTorch
(train_set, valid_set, test_set), info = load_dataset(
    "blink",
    mode="pytorch",
    percent_train=0.4,
    percent_val=0.4,
    image_size=image_size,
    with_info=True,
)

# list of classes as string from  dataset
label_names = info["classes"]
print("Classes in dataset: {}".format(label_names))

# build model
model = Model(len(label_names))
# and train it
model.train(train_set, valid_set, batch_size=32, nepochs=2)

# test prediction on one test batch:
test_loader = torch.utils.data.DataLoader(test_set, batch_size=32)
for images, labels in test_loader:  # Only take a single batch
    predictions = model.predict(images)

    # get correct and incorrect predictions
    correct = predictions == labels
    incorrect = predictions != labels

    print(
        "Evaluation: {} correct predictions and {} incorrect".format(
            sum(correct), sum(incorrect)
        )
    )
    break

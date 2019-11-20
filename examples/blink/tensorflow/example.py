from os import path
from pathlib import Path
import glob

from model import Model
import deel.datasets.blink.tensorflow as dataset

if __name__ == '__main__':    
    train_set, valid_set, x_test, y_test, label_names = dataset.load(forceDownload=False, percent_train=40, percent_val=40)

    aModel = Model()
    aModel.train(train_set, valid_set, label_names, epochs=1)
    aModel.save("yolo")
    #aModel.load(name="yolo")

    print(label_names)
    # Prediction on 1 image
    img_path = x_test[0]
    pred_index = aModel.predict(img_path)
    print(label_names[pred_index], ":", img_path)

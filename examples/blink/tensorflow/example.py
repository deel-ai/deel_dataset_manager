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
    _DEELDATASET_BASE_DIR = str(Path.home().joinpath('.deeldataset'))

    # Prediction on 1 image
    img_path = path.join(_DEELDATASET_BASE_DIR, "blink", "blink-3.0-20191004.zip_extracted", "final_db_anonymous", "noblink", "nb_8.bmp")
    pred_index = aModel.predict(img_path)
    print(label_names[pred_index])

    # Prediction overall image inside blink_right folder
    images = [f for f in glob.glob(path.join(_DEELDATASET_BASE_DIR, "blink", "blink-3.0-20191004.zip_extracted", "final_db_anonymous", "blink_right", "*.bmp"), recursive=True)]
    for cur_img in images:
        pred_index = aModel.predict(cur_img)
        print(label_names[pred_index])

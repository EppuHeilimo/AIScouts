import os, sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from MachineLearning.model import Model

paths = ['/Car/', '/Park/']
data_folder = "/media/cf2017/levy/tensorflow/parking_place2/"
mod = Model(paths, learning_rate=0.001, layers=4, epochs=10,
           data_folder=data_folder, model_name='park_model' + str(26))
mod.train_model(saved_train_data_path=data_folder + "park_model23/", separate_validation_data=True)

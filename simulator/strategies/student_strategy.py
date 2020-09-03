import numpy as np
from tensorflow.python.keras.models import load_model

from .auto_pilot import AutoSteer
from joblib import load
import os

class AutoSteerStudent(AutoSteer):
    pass

    ######## skLearn implementation#################
    def __init__(self):
        self.clf = load(os.path.join('..', 'models', 'auto_pliot.joblib'))


    def steer(self,view):
        reduce_camera_image = 5
        width = view.shape[1]
        height = view.shape[0]
        dim = (int(width / reduce_camera_image), int(height / reduce_camera_image))
        camera_view_reduced = view[::reduce_camera_image, ::reduce_camera_image]
        size_array = dim[0] * dim[1] * 3  # width height time 3 channels
        image_data = camera_view_reduced.reshape(1, size_array)
        prediction = self.clf.predict(image_data)
        print(prediction)
        if prediction[0] == 0:
            return 'forward'
        elif prediction[0] == 1:
            return 'left'
        elif prediction[0] == 2:
            return 'right'
        else:
            return 'forward'

    ################## Keras deeplearning implementation ###################################
    # def __init__(self):
    #     self.model = load_model(os.path.join('..', 'models', 'my-keras-model.h5'))
    #
    # def steer(self,view):
    #     reduce_camera_image = 5
    #     width = view.shape[1]
    #     height = view.shape[0]
    #     dim = (int(width / reduce_camera_image), int(height / reduce_camera_image))
    #     camera_view_reduced = view[::reduce_camera_image, ::reduce_camera_image]
    #     camera_view_reduced = np.array([camera_view_reduced.astype('float32') / 255 ])
    #     prediction = self.model.predict_classes(camera_view_reduced)[0]
    #     print(prediction)
    #     if prediction == 0:
    #         return 'forward'
    #     elif prediction == 1:
    #         return 'left'
    #     elif prediction == 2:
    #         return 'right'
    #     else:
    #         return 'forward'
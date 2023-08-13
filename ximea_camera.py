import numpy as np
from ximea import xiapi
import cv2
from ctypes import *

def undistort(image):
    with np.load('calibration_parameters_2.npz') as X:
        mtx, dist = X['mtx'], X['dist']

    # Assuming that 'img' is your distorted image
    h, w = image.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

    # Undistort
    dst = cv2.undistort(image, mtx, dist, None, newcameramtx)
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    return dst

def get_camera():
    # create instance for first connected camera
    cam = xiapi.Camera()

    # start communication
    # to open specific device, use:
    # cam.open_device_by_SN('41305651')
    # (open by serial number)
    print('Opening first camera...')
    cam.open_device()

    # settings
    cam.set_exposure(45000)
    cam.set_param('imgdataformat', "XI_RGB32")
    cam.set_param("auto_wb", 1)
    print('Exposure was set to %i us' % cam.get_exposure())

    # start data acquisition
    print('Starting data acquisition...')
    cam.start_acquisition()

    return cam



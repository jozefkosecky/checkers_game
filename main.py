from logging import root
import tkinter
import cv2
from ximea import xiapi
import numpy as np
import ximea_camera
import board_detection


def main():
    # create instance of Image to store image data and metadata
    cam = ximea_camera.get_camera()  # call your function with module name prefix
    img = xiapi.Image()
    
    number_of_triming = 0
    while 1:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

        cam.get_image(img)
        image = img.get_image_data_numpy(invert_rgb_order=False)
        
        image = cv2.resize(image, (600, 600))
        
        undistort_image = ximea_camera.undistort(image)
        cv2.imshow("undistort_image", undistort_image)

        if key == ord(' '):
             cv2.imwrite("image_2.jpg", undistort_image)

    
        if(number_of_triming == 0):
            number_of_triming = board_detection.get_number_of_triming(undistort_image)

        trimmed_image = None
        for trim in range(number_of_triming):
            if(trimmed_image is None):
                image_for_trim = undistort_image
            else:
                image_for_trim = trimmed_image
            trimmed_image = board_detection.trim_chessboard(image_for_trim)

        cv2.imshow("trimmed_image", trimmed_image)


    # stop data acquisition
    print('Stopping acquisition...')
    cam.stop_acquisition()

    # stop communication
    cam.close_device()

    print('Done.')


if __name__ == '__main__':
    main()

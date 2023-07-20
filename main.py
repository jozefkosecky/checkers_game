import cv2
from ximea import xiapi
import numpy as np
import ximea_camera


def main():
    # create instance of Image to store image data and metadata
    cam = ximea_camera.get_camera()  # call your function with module name prefix
    img = xiapi.Image()

    with np.load('calibration_parameters.npz') as X:
            mtx, dist = X['mtx'], X['dist']

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
             cv2.imwrite("image.jpg", undistort_image)

    # stop data acquisition
    print('Stopping acquisition...')
    cam.stop_acquisition()

    # stop communication
    cam.close_device()

    print('Done.')


if __name__ == '__main__':
    main()

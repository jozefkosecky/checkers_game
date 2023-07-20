import cv2
from ximea import xiapi
import numpy as np
import ximea_camera


cam = ximea_camera.get_camera()  # call your function with module name prefix
img = xiapi.Image()

counter = 0
imageName = "camera"

while counter != 50 :
    cam.get_image(img)
    image = img.get_image_data_numpy(invert_rgb_order=False)
    image = cv2.resize(image, (600, 600))
    cv2.imshow("test", image)
    key = cv2.waitKey(1)

    if key == ord(' '):
        print("Hej")
        filename ="images_for_calibration/" + imageName + "{}.jpg".format(counter)
        cv2.imwrite(filename, image)
        counter += 1
        print("Saved image to {}".format(filename))
    elif key == ord('q'):
        break



# stop data acquisition
print('Stopping acquisition...')
cam.stop_acquisition()

# stop communication
cam.close_device()

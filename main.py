from logging import root
import threading
import tkinter
import cv2
from ximea import xiapi
import numpy as np
import ximea_camera
import board_detection
import concurrent.futures
import game
from operator import itemgetter

def main():
    # create instance of Image to store image data and metadata
    cam = ximea_camera.get_camera()  # call your function with module name prefix
    img = xiapi.Image()
    
    bounderies = None
    createTrackBars = True

    init = True

    number_of_occupancy = 40
    game_board = None
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
             cv2.imwrite("trimmed_image.jpg", trimmed_image)

    
        if(bounderies is None):
            bounderies = board_detection.get_trim_param(undistort_image)

        trimmed_image = undistort_image.copy()
        for boundery in bounderies:
            # Get the bounding rectangle for the largest contour
            x, y, w, h = cv2.boundingRect(boundery)

            # Crop the image using the bounding rectangle
            trimmed_image = trimmed_image[y:y+h, x:x+w]
        
        cv2.imshow("trimmed_image", trimmed_image)

        if(init):
            all_contours = board_detection.get_contours_off_all_rectangles(trimmed_image)
            sorted_all_contours = board_detection.sorted_coordinates(all_contours)
        else:
            isHandAboveImage = board_detection.is_hand_above_image(trimmed_image, number_of_occupancy)
            if(isHandAboveImage):
                # print("RUKA")
                continue
            else:
                game_board = game.checker_game(possible_moves, game_board)
                
    
        occupancy_contours = board_detection.get_occupancy(trimmed_image, createTrackBars, number_of_occupancy, init)


        possible_moves = board_detection.get_possible_moves(sorted_all_contours, occupancy_contours, trimmed_image)
        possible_moves = np.reshape(possible_moves, (8, 8))
        # print(possible_moves)

        if(init):
            createTrackBars = False
            init = False



    # stop data acquisition
    print('Stopping acquisition...')
    cam.stop_acquisition()

    # stop communication
    cam.close_device()

    print('Done.')


if __name__ == '__main__':
    main()

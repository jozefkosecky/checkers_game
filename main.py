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
    was_move_made = False
    player = 1
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
            
        trimmed_image = cv2.rotate(trimmed_image, cv2.ROTATE_180)
        cv2.imshow("trimmed_image", trimmed_image)

        if(init):
            all_contours = board_detection.get_contours_off_all_rectangles(trimmed_image)
            sorted_all_contours = board_detection.sorted_coordinates(all_contours)
            init = False

            occupancy_contours = board_detection.get_occupancy(trimmed_image, createTrackBars, number_of_occupancy)
            possible_moves = board_detection.get_possible_moves(sorted_all_contours, occupancy_contours, trimmed_image)
            possible_moves = np.reshape(possible_moves, (8, 8))
            createTrackBars = False
        else:
            isHandAboveImage = board_detection.is_hand_above_image(trimmed_image, number_of_occupancy)

            occupancy_contours = board_detection.get_occupancy(trimmed_image, createTrackBars, number_of_occupancy)
            possible_moves = board_detection.get_possible_moves(sorted_all_contours, occupancy_contours, trimmed_image)
            possible_moves = np.reshape(possible_moves, (8, 8))
            
            # isHandAboveImage = False
            if(isHandAboveImage):
                print("RUKA")
                was_move_made = True
                continue
            else:      
                if(was_move_made):
                    print("\n\n\n\n\n\n\n\n\n\n")

                if(game_board is None):
                    game_board = game.create_checkers_board(possible_moves)
                    print_game_board(possible_moves, game_board, player)
                
                if(was_move_made):
                    who_made_move = game.who_made_move(possible_moves, game_board)
                    if(who_made_move is None):
                        if(player == 1):
                            print_game_board(possible_moves, game_board, 2)
                        else:
                            print_game_board(possible_moves, game_board, 1)
                        print("Caka sa na tah od hraca: " + str(player))
                    else:
                        game_board = game.update_checkers_board(possible_moves, game_board)
                        print_game_board(possible_moves, game_board, player)
                        if(who_made_move == 1):
                            player = 2
                            print("Caka sa na tah od hraca: " + str(player))
                        else:
                            player = 1
                            print("Caka sa na tah od hraca: " + str(player))
                    was_move_made = False
                
            



    # stop data acquisition
    print('Stopping acquisition...')
    cam.stop_acquisition()

    # stop communication
    cam.close_device()

    print('Done.')


def print_game_board(possible_moves, game_board, player):
    print("Hracia doska po tahu od hraca: " + str(player) +"\n")
    print("Possible moves \n")
    print(possible_moves)
    print("\n")

    print("Game board \n")
    print(game_board)
    print("\n")


if __name__ == '__main__':
    main()

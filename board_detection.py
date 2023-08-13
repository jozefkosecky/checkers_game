import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk



def nothing(x):
    pass

def get_trim_param(undistort_image):
    trimmed_image = undistort_image
    bounderies = []
    while 1:
        bounderies.append(get_bounderies(trimmed_image)) 
        
        # Get the bounding rectangle for the largest contour
        x, y, w, h = cv2.boundingRect(bounderies[-1])

        # Crop the image using the bounding rectangle
        trimmed_image = trimmed_image[y:y+h, x:x+w]

        cv2.imshow("trimming", trimmed_image)

        key = cv2.waitKey(0)
        if key == 27:
            cv2.destroyWindow("trimming")
            break


    
    return bounderies
            
def get_bounderies(image):  # Remove argument here
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold the image to separate the black frame
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours by area and keep the largest one
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    return contours[0]


def color_white_stones(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)

    canny = cv2.Canny(blurred, 223, 1, 1)

    kernel = np.ones((2,2),np.uint8)
    dilate = cv2.dilate(canny,kernel,iterations = 1)

    contours = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    img_copy = image.copy()
    for c in contours:
        cv2.drawContours(img_copy, [c], -1, (40, 40, 40), -1)

    return img_copy

def highlight_black_rectangles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Closing
    kernel = np.ones((39,31),np.uint8)
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Dilate
    kernel = np.ones((10,10),np.uint8)
    dilate = cv2.dilate(closing,kernel,iterations = 1)

    cv2.imshow("dilate", dilate)
    imagem = cv2.bitwise_not(dilate)

    canny = cv2.Canny(imagem, 120, 255, 1)

    # Dilate
    kernel = np.ones((2,2),np.uint8)
    dilate = cv2.dilate(canny,kernel,iterations = 1)

    

    contours = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    result = image.copy()
    for c in contours:
        cv2.drawContours(result, [c], -1, (0, 0, 255), 2)
    
    return result

def get_contours_off_all_rectangles(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    attempts = 1
    param1 = 255
    while 1:
        if(param1 < 1):
            attempts += 1
            if(attempts > 1):
                break
            
        blur_copy = np.copy(edges)

        param1 -= 1

        # Detect lines using the Hough Line Transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, param1)

        # Create a copy of the original image to draw lines on
        black_image = image.copy()
        black_image = np.zeros_like(black_image)

        # Draw the lines on the image
        if lines is not None:
            for rho, theta in lines[:, 0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * a)
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * a)

                cv2.line(black_image, (x1, y1), (x2, y2), (255, 255, 255), 2)


        canny = cv2.Canny(black_image, 120, 255, 1)

        gray = cv2.cvtColor(black_image, cv2.COLOR_RGB2GRAY)

        cv2.imshow("all_rectangles_black_image", gray)

        # Find contours
        contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Filter for rectangles
        rectangles = []
        for cnt in contours:
            # Get convex hull
            hull = cv2.convexHull(cnt)
            
            # Get approximate polygon
            epsilon = 0.02 * cv2.arcLength(hull, True)
            approx = cv2.approxPolyDP(hull, epsilon, True)
            
            # Check if it is a rectangle
            if len(approx) == 4:
                rectangles.append(approx)


        # Sort the contours by area and keep the largest one
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        new_image = image.copy()
        if(len(contours) >= 64 and len(contours) <= 150):
            correct_result = 0
            new_contours = []
            for position in range(1, len(contours)):

                x,y,w,h = cv2.boundingRect(contours[position])
            
                if(w > 20 and h > 20 and correct_result < 64):
                    new_contours.append(contours[position])
                    correct_result += 1
                    cv2.rectangle(new_image, (x, y), (x + w, y + h), (36,255,12), 1)
            # cv2.drawContours(result, [contours[position]], -1, (0, 0, 255), 2)

            cv2.imshow('all_rectangles_new_image', new_image)
            if(correct_result == 64):
                break

    return new_contours


#################### GET OCCUPANCY AUTOMATIC ###################################
occupancy_canny_param1 = 1
occupancy_canny_param2 = 1

def get_occupancy(image, createTrackBars, number_of_occupancy):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Blur
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    cv2.imshow('Occupancy_canny', blur)

    if(createTrackBars):
        # create trackbars for color change
        cv2.createTrackbar('param1','Occupancy_canny',1,100,nothing) #50
        cv2.setTrackbarMin('param1','Occupancy_canny', 1)
        cv2.createTrackbar('param2','Occupancy_canny',1,100,nothing) #10
        cv2.setTrackbarMin('param2','Occupancy_canny', 1)

    occupancy_canny_param1 = cv2.getTrackbarPos('param1','Occupancy_canny')
    occupancy_canny_param2 = cv2.getTrackbarPos('param2','Occupancy_canny')

    while 1:

        if(createTrackBars == True):
            cv2.setTrackbarPos('param1','Occupancy_canny', occupancy_canny_param1)
            cv2.setTrackbarPos('param2','Occupancy_canny', occupancy_canny_param2)

        # Canny
        edges = cv2.Canny(blur,occupancy_canny_param1,occupancy_canny_param2,apertureSize=3)
        cv2.imshow("Occupancy_canny", edges)

        imagem = cv2.bitwise_not(edges)
        cv2.imshow("Occupancy_imagem", imagem)

        # Closing
        kernel = np.ones((30,30),np.uint8)
        closing = cv2.morphologyEx(imagem, cv2.MORPH_OPEN, kernel)
        cv2.imshow("Occupancy_closing", closing)

        contours = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        # print("Occupancy: " + str(len(contours)))
        result = image.copy()
        for c in contours:
            area = cv2.contourArea(c)
            cv2.drawContours(result, [c], -1, (0, 255, 0), 2)

        cv2.imshow('Occupancy_result', result)

        if(createTrackBars == False or len(contours) == number_of_occupancy):
            # print("Occupancy: " + str(len(contours)))
            break
        
        occupancy_canny_param1 += 1
        if(occupancy_canny_param1 == 100):
            occupancy_canny_param1 = 1
            occupancy_canny_param2 += 1

        if(occupancy_canny_param2 == 100):
            occupancy_canny_param1 = 1
            occupancy_canny_param2 = 1
            break

        
    return contours


#################### GET OCCUPANCY MANUAL ###################################
# occupancy_canny_param1 = 70
# occupancy_canny_param2 = 1

# def get_occupancy(image, createTrackBars):
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     # Blur
#     blur = cv2.GaussianBlur(gray, (5,5), 0)
#     cv2.imshow('Occupancy_canny', blur)

#     if(createTrackBars):
#         # create trackbars for color change
#         cv2.createTrackbar('param1','Occupancy_canny',50,100,nothing)
#         cv2.setTrackbarMin('param1','Occupancy_canny', 1)
#         cv2.createTrackbar('param2','Occupancy_canny',10,200,nothing)
#         cv2.setTrackbarMin('param2','Occupancy_canny', 1)

#     # get current positions of four trackbars
#     occupancy_canny_param1 = cv2.getTrackbarPos('param1','Occupancy_canny')
#     occupancy_canny_param2 = cv2.getTrackbarPos('param2','Occupancy_canny')

#     # Canny
#     edges = cv2.Canny(blur,occupancy_canny_param1,occupancy_canny_param2,apertureSize=3)
#     cv2.imshow("Occupancy_canny", edges)

#     imagem = cv2.bitwise_not(edges)

#     # Closing
#     kernel = np.ones((30,30),np.uint8)
#     closing = cv2.morphologyEx(imagem, cv2.MORPH_OPEN, kernel)

#     contours = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#     contours = contours[0] if len(contours) == 2 else contours[1]

#     result = image.copy()
#     for c in contours:
#         area = cv2.contourArea(c)
#         cv2.drawContours(result, [c], -1, (0, 255, 0), 1)

#     cv2.imshow('result', result)
#     return contours

def sorted_coordinates(all_contours):
    array_2d_in_2d = []
    position = 0
    if(len(all_contours) == 64):
        for i in range(8):
            inner_array = []
            for j in range(8):
                x, y, w, h = cv2.boundingRect(all_contours[position])
                inner_2d_array = [x, y, w, h]
                inner_array.append(inner_2d_array)
                position += 1
            array_2d_in_2d.append(inner_array)

        # print("Zaciatok [\n")
        # for i, row in enumerate(array_2d_in_2d):
        #     print(" ", row, end="")
        #     if i < len(array_2d_in_2d) - 1:
        #         print(",")
        #     else:
        #         print("")
        # print("]\n")
        # print("\n\n\n")

    # Flattening the array
    flattened_coordinates_with_wh = [coordinate for sublist in array_2d_in_2d for coordinate in sublist]

    # Sorting by y first, then by x, ignoring w and h
    sorted_coordinates = sorted(flattened_coordinates_with_wh, key=lambda x: (x[1], x[0]))
    return sorted_coordinates

def get_possible_moves(all_rectangles, occupancy_rectagles, image):
    possible_moves = []
    possible_move_was_found = False
    for position in range(len(all_rectangles)):

        isRectangleBlack = is_rectangle_black(image, all_rectangles[position])

        if(isRectangleBlack):
            for occupancy_rectagle in occupancy_rectagles:
                x, y, w, h = cv2.boundingRect(occupancy_rectagle)
                point_x = get_center_of_rectangle(x, w)
                point_y = get_center_of_rectangle(y, h)

                isPointInRectangle = is_point_in_rectangle(all_rectangles[position], point_x, point_y)
            
                if(isPointInRectangle):
                    possible_move_was_found = True
                    break
        
        if(possible_move_was_found and isRectangleBlack):
            # possible_moves.append(all_rectangles[position])
            possible_moves.append(3)
            x, y, w, h = all_rectangles[position]
            point_x = get_center_of_rectangle(x, w)
            point_y = get_center_of_rectangle(y, h)
            image = cv2.circle(image, (int(point_x), int(point_y)), radius=4, color=(0, 0, 255), thickness=-1)
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
        else:
            # possible_moves.append(None)
            possible_moves.append(0)

        cv2.imshow('possible_moves', image)
        possible_move_was_found = False

    return possible_moves

def is_point_in_rectangle(rectangle, point_x, point_y):
    rectangle_top_left_x, rectangle_top_left_y, width, height = rectangle
    rectangle_bottom_right_x = rectangle_top_left_x + width
    rectangle_bottom_right_y = rectangle_top_left_y + height

    if rectangle_top_left_x <= point_x <= rectangle_bottom_right_x and rectangle_top_left_y <= point_y <= rectangle_bottom_right_y:
        return True
    else:
        return False
    
def get_center_of_rectangle(point, lenght):
    return point + (lenght / 2)

def is_rectangle_black(img, rectangle, threshold=127):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    top_left_x, top_left_y, width, height = rectangle
    # Slice the rectangle from the image
    rectangle = thresh[top_left_y:top_left_y+height, top_left_x:top_left_x+width]
    
    # Calculate the mean value in the rectangle
    mean_value = np.mean(rectangle)

    # Compare the mean value to the threshold
    if mean_value < threshold:
        return True
    else:
        return False
    

def is_hand_above_image(image, number_of_occupancy):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Blur
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # print("HAND")

    occupancy_canny_param1 = cv2.getTrackbarPos('param1','Occupancy_canny')
    occupancy_canny_param2 = cv2.getTrackbarPos('param2','Occupancy_canny')

     # Canny
    edges = cv2.Canny(blur,occupancy_canny_param1,occupancy_canny_param2,apertureSize=3)
    cv2.imshow("Occupancy_canny", edges)

    imagem = cv2.bitwise_not(edges)

    # Closing
    kernel = np.ones((30,30),np.uint8)
    closing = cv2.morphologyEx(imagem, cv2.MORPH_OPEN, kernel)

    contours = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    # print("Hand: " + str(len(contours)) + " - " + str(number_of_occupancy))
    if(len(contours) != number_of_occupancy):
        return True
    return False
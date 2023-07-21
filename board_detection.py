import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk

def get_number_of_triming(undistort_image):
    number_of_triming = 0
    trimmed_image = None
    while 1:
        if(trimmed_image is None):
            image_for_trim = undistort_image
        else:
            image_for_trim = trimmed_image
        trimmed_image = trim_chessboard(image_for_trim)
        cv2.imshow("trimming", trimmed_image)
        key = cv2.waitKey(0)
        if key == 27:
            number_of_triming += 1
            cv2.destroyWindow("trimming")
            break
        else:
            number_of_triming += 1

    return number_of_triming
            
def trim_chessboard(image):  # Remove argument here
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Threshold the image to separate the black frame
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours by area and keep the largest one
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Get the bounding rectangle for the largest contour
    x, y, w, h = cv2.boundingRect(contours[0])

    # Crop the image using the bounding rectangle
    cropped_image = image[y:y+h, x:x+w]

    return cropped_image


def color_white_stones(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5,5), 0)

    canny = cv2.Canny(blurred, 200, 1, 1)

    kernel = np.ones((2,2),np.uint8)
    dilate = cv2.dilate(canny,kernel,iterations = 1)

    contours = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    img_copy = image.copy()
    for c in contours:
        cv2.drawContours(img_copy, [c], -1, (50, 50, 50), -1)

    return img_copy

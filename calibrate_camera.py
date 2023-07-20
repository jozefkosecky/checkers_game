import numpy as np
import cv2 as cv
import glob
import matplotlib.pyplot as plt

chessboardSize = (7, 7)
frameSize = (600, 600)

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('images_for_calibration/*.jpg')

for image in images:
    print(image)
    img = cv.imread(image)
    # cropped_image = img[75:475, 100:600]
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # plt.imshow(cropped_image, cmap="gray", vmin=0, vmax=255)
    # plt.show()
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, chessboardSize, None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv.imshow('img', img)
        cv.waitKey(200)

cv.destroyAllWindows()

############ Calibration ######################

img = cv.imread('images_for_calibration/camera49.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, cameraMatrix, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("cameraMatrix:", cameraMatrix)
print("fx:", cameraMatrix.item(0, 0), "fy:", cameraMatrix.item(1, 1))
print("cx:", cameraMatrix.item(0, 2), "cy:", cameraMatrix.item(1, 2))
# print("Distortion parameters:", dist)
# print("Rotation vectors:", rvecs)
# print("Translation vectors:", tvecs)

############ Undistortion ######################


cv.imshow("images_for_calibration/camera49.jpg", img)
h,  w = img.shape[:2]
print("image size", img.shape[::-1])
print("h", h)
print("w", w)
newCameraMatrix, roi = cv.getOptimalNewCameraMatrix(cameraMatrix, dist, (w, h), 1, (w, h))


# Undistort
dst = cv.undistort(img, cameraMatrix, dist, None, newCameraMatrix)
# crop the image
x, y, w, h = roi
print("roi", roi)
dst = dst[y:y + h, x:x + w]
cv.imwrite('calibrated_images/calibResult1.png', dst)
# img2 = cv.imread('calibResult1.jpg')
# cv.imshow("calibResult1.jpg", img2)

# Undistort with remapping
h,  w = img.shape[:2]
mapx, mapy = cv.initUndistortRectifyMap(cameraMatrix, dist, None, newCameraMatrix, (w, h), 5)
dst = cv.remap(img, mapx, mapy, cv.INTER_LINEAR)
# crop the image
x, y, w, h = roi
dst = dst[y:y + h, x:x + w]
cv.imwrite('calibrated_images/calibResult2.png', dst)

# Reprojection error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], cameraMatrix, dist)
    error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2) / len(imgpoints2)
    mean_error += error

print("total error: {}".format(mean_error / len(objpoints)))

# Assuming that 'mtx' is your camera matrix and 'dist' is your distortion coefficients
np.savez('calibration_parameters_2.npz', mtx=cameraMatrix, dist=dist)

cv.waitKey(0)
cv.destroyAllWindows()

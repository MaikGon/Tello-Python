import cv2
import numpy as np
import time
import socket
from djitellopy import tello


me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

hsv_Vals = [0, 0, 158, 179, 255, 255]


def thresholding(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv_Vals[0], hsv_Vals[1], hsv_Vals[2]])
    upper = np.array([hsv_Vals[3], hsv_Vals[4], hsv_Vals[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


def contours(img_th, img):
    cnt, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, cnt, -1, (255, 255, 0), 7)


while True:
    cap = me.get_frame_read().frame
    img = cv2.resize(cap, (480, 360))
    # img = cv2.flip(img, 0)

    imgThresh = thresholding(img)

    cv2.imshow('Output', img)
    cv2.imshow('Path', imgThresh)
    cv2.waitKey(1)



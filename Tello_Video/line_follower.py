import cv2
import numpy as np
from djitellopy import tello
import time


me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()


#hsv_Vals = [0, 0, 158, 179, 255, 255]
#hsv_Vals = [40, 0, 0, 179, 38, 255]
hsv_Vals = [0, 160, 11, 179, 255, 255]

num_sensors = 3
th_value = 0.4
width, height = 480, 360
sensitivity = 3
weights = [25, 15, 0, -15, -25]
up_down = 0
lSpeed = 20
repeat = False


def thresholding(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv_Vals[0], hsv_Vals[1], hsv_Vals[2]])
    upper = np.array([hsv_Vals[3], hsv_Vals[4], hsv_Vals[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


def contours(img_th, img):
    cnt, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cy = 0
    try:
        biggest = max(cnt, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w//2
        cy = y + h//2
        cv2.drawContours(img, biggest, -1, (255, 255, 0), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    except:
        pass
    print(cy)
    return cy


def getSensorOut(imgThresh, num_sensors):
    imgs = np.vsplit(imgThresh, num_sensors)
    pixels = (imgThresh.shape[1]//num_sensors) * imgThresh.shape[0]
    sensor_out = []
    for num, im in enumerate(imgs):
        cnt_pixels = cv2.countNonZero(im)
        if cnt_pixels > th_value*pixels:
            sensor_out.append(1)
        else:
            sensor_out.append(0)
        cv2.imshow(str(num), im)
    # print(sensor_out)

    #if sensor_out == [0, 0, 0]:
        #me.land()
    return sensor_out


def send_commands(sensor_out):
    global up_down, repeat

    if sensor_out != [0, 0, 0]:
        repeat = False

    # Translation
    if sensor_out == [1, 0, 0]:
        up_down = weights[0]
    elif sensor_out == [1, 1, 0]:
        up_down = weights[1]
    elif sensor_out == [0, 1, 0]:
        up_down = weights[2]
    elif sensor_out == [0, 1, 1]:
        up_down = weights[3]
    elif sensor_out == [0, 0, 1]:
        up_down = weights[4]

    elif sensor_out == [0, 0, 0] and repeat is False:
        repeat = True
        if up_down > 0:
            up_down = weights[3]
        elif up_down < 0:
            up_down = weights[1]
    elif sensor_out == [0, 0, 0] and repeat is True:
        pass

    elif sensor_out == [1, 1, 1]:
        up_down = weights[2]
    elif sensor_out == [1, 0, 1]:
        up_down = weights[2]
    print(lSpeed, 0, up_down, 0)
    me.send_rc_control(lSpeed, 0, up_down, 0)


takeoff = False
while True:
    cap = me.get_frame_read().frame
    img = cv2.resize(cap, (width, height))
    #img = cv2.flip(img, 0)
    if takeoff is False:
        takeoff = True
        me.takeoff()

    imgThresh = thresholding(img)
    #cy = contours(imgThresh, img)

    sensor_out = getSensorOut(imgThresh, num_sensors)
    send_commands(sensor_out)

    cv2.imshow('Output', img)
    #cv2.imshow('Path', imgThresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

me.land()
cv2.destroyAllWindows()



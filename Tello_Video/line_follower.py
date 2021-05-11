import cv2
import numpy as np
from djitellopy import tello
import time


drone = tello.Tello()
drone.connect()
print('Battery: ', drone.get_battery())
drone.streamon()


hsv_Vals = [0, 160, 11, 179, 255, 255]

num_sensors = 3
th_value = 0.1
width, height = 480, 360
sensitivity = 3
weights = [20, 15, 0, -15, -20]
up_down = 0
lSpeed = 20
repeat = False


def threshold(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv_Vals[0], hsv_Vals[1], hsv_Vals[2]])
    upper = np.array([hsv_Vals[3], hsv_Vals[4], hsv_Vals[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


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

    return sensor_out


def send_commands(sensor_out):
    global up_down, repeat

    if sensor_out != [0, 0, 0]:
        repeat = False

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
    drone.send_rc_control(lSpeed, 0, up_down, 0)


takeoff = False
while True:
    cap = drone.get_frame_read().frame
    img = cv2.resize(cap, (width, height))

    if takeoff is False:
        takeoff = True
        drone.takeoff()
        time.sleep(1)

    imgThresh = threshold(img)

    sensor_out = getSensorOut(imgThresh, num_sensors)
    send_commands(sensor_out)

    cv2.imshow('Img', img)
    #cv2.imshow('Img_thresh', imgThresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

drone.land()
cv2.destroyAllWindows()



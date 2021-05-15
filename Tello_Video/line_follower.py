import cv2
import numpy as np
from djitellopy import tello
import time


drone = tello.Tello()
drone.connect()
print('Battery: ', drone.get_battery())
drone.streamon()


hsv_Vals_red_line = [0, 160, 11, 179, 255, 255]

# DOSTROIC DO KONTROLI ODLEGLOSCI OD SCIANY
hsv_Vals_markers = [0, 160, 11, 179, 255, 255]
distance_control_minV = 0
distance_control_maxV = 1000


num_sensors = 3
th_value = 0.1
width, height = 480, 360
sensitivity = 3
weights = [20, 15, 0, -15, -20]
up_down = 0
lSpeed = 20
repeat = False


def threshold(img, thresh):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([thresh[0], thresh[1], thresh[2]])
    upper = np.array([thresh[3], thresh[4], thresh[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


def contours(img_th, img):
    cnt, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, cnt, -1, (255, 255, 0), 7)
    cx = 0
    try:
        biggest = max(cnt, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w//2
        cy = y + h//2
        cv2.drawContours(img, biggest, -1, (255, 255, 0), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    except:
        pass
    return w, h


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




def distance_control(m_width, m_height, min_val, max_val):

    param = max([m_width, m_height])

    if param <= min_val:
        pass
        # lec do przodu
    elif param >= max_val:
        pass
        # lec do tylu
    else:
        pass
        # jest git, tak trzymaj



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

    imgThresh = threshold(img, hsv_Vals_red_line)
    markerImage = threshold(img, hsv_Vals_markers)

    sensor_out = getSensorOut(imgThresh, num_sensors)
    send_commands(sensor_out)

    marker_width, marker_height = contours(markerImage, img)
    distance_control(marker_height, marker_width, distance_control_minV, distance_control_maxV)


    cv2.imshow('Img', img)
    #cv2.imshow('Img_thresh', imgThresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

drone.land()
cv2.destroyAllWindows()



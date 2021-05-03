import cv2
import numpy as np
from djitellopy import tello


me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
# me.takeoff()

hsv_Vals = [0, 0, 158, 179, 255, 255]
num_sensors = 3
th_value = 0.3
width, height = 480, 360
sensitivity = 3
weights = [-25, -15, 0, 15, 25]
curve = 0
fSpeed = 10


def thresholding(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsv_Vals[0], hsv_Vals[1], hsv_Vals[2]])
    upper = np.array([hsv_Vals[3], hsv_Vals[4], hsv_Vals[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


def contours(img_th, img):
    cnt, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
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
    return cx


def getSensorOut(imgThresh, num_sensors):
    imgs = np.hsplit(imgThresh, num_sensors)
    pixels = (imgThresh.shape[1]//num_sensors) * imgThresh.shape[0]
    sensor_out = []
    for num, im in enumerate(imgs):
        cnt_pixels = cv2.countNonZero(im)
        if cnt_pixels > th_value*pixels:
            sensor_out.append(1)
        else:
            sensor_out.append(0)
        cv2.imshow(str(num), im)
    print(sensor_out)

    return sensor_out


def send_commands(sensor_out, cx):
    global curve
    # Translation
    lr = (cx - width//2) // sensitivity
    lr = int(np.clip(lr, -10, 10))

    if 2 > lr > -2:
        lr = 0

    # Rotation
    if sensor_out == [1, 0, 0]:
        curve = weights[0]
    elif sensor_out == [1, 1, 0]:
        curve = weights[1]
    elif sensor_out == [0, 1, 0]:
        curve = weights[2]
    elif sensor_out == [0, 1, 1]:
        curve = weights[3]
    elif sensor_out == [0, 0, 1]:
        curve = weights[4]
    elif sensor_out == [0, 0, 0]:
        curve = weights[2]
    elif sensor_out == [1, 1, 1]:
        curve = weights[2]
    elif sensor_out == [1, 0, 1]:
        curve = weights[2]
    print(lr, fSpeed, 0, curve)
    # me.send_rc_control(lr, fSpeed, 0, curve)


while True:
    cap = me.get_frame_read().frame
    img = cv2.resize(cap, (width, height))
    img = cv2.flip(img, 0)

    imgThresh = thresholding(img)
    cx = contours(imgThresh, img)

    sensor_out = getSensorOut(imgThresh, num_sensors)
    send_commands(sensor_out, cx)

    cv2.imshow('Output', img)
    cv2.imshow('Path', imgThresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()



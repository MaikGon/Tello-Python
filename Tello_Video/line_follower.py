import cv2
import numpy as np
from djitellopy import tello
import time
from video_mod import VideoOut


drone = tello.Tello()
drone.connect()
print('Battery: ', drone.get_battery())
drone.streamon()

vid = VideoOut("out3", 'mp4', 480, 360, 30)
hsv_Vals_red_line = [0, 160, 11, 179, 255, 255]

hsv_Vals_markers = [20, 99, 180, 40, 255, 255]
distance_control_minV = 40
distance_control_maxV = 80


num_sensors = 3
th_value = 0.1
width, height = 480, 360
sensitivity = 3
weights = [20, 15, 0, -20, -25]
up_down = 0
lSpeed = 20
repeat = False
fb = 0


def threshold(img, thresh):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([thresh[0], thresh[1], thresh[2]])
    upper = np.array([thresh[3], thresh[4], thresh[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask


def contours(img_th, img):
    cnt, _ = cv2.findContours(img_th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img, cnt, -1, (255, 255, 0), 7)
    square_cnt = []
    for c in cnt:
        xt, yt, wt, ht = cv2.boundingRect(c)
        if wt == ht:
            square_cnt.append(c)

    try:
        biggest = max(square_cnt, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(biggest)
        cx = x + w//2
        cy = y + h//2
        cv2.drawContours(img, biggest, -1, (255, 255, 0), 7)
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        if w >= 25 and h >= 25:
            return w, h
        else:
            return 0, 0
    except:
        return 0, 0


def getSensorOut(imgThresh, num_sensors):
    # horizontal
    img_copy = imgThresh.copy()
    imgs_horizontal = np.hsplit(img_copy, 5)
    central_imgs = [imgs_horizontal[1], imgs_horizontal[2], imgs_horizontal[3]]
    final_img = cv2.hconcat(central_imgs)

    #vertical
    imgs = np.vsplit(final_img, num_sensors)
    pixels = (final_img.shape[1]//num_sensors) * final_img.shape[0]
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
    global fb
    param = max([m_width, m_height])
    print('param', param)
    if param != 0:
        if param <= min_val:
            fb = 20
        elif param >= max_val:
            fb = -20
        else:
            fb = 0
    else:
        fb = -20


def send_commands(sensor_out):
    global up_down, repeat, fb

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
        fb = 0
        repeat = True
        if up_down > 0:
            up_down = weights[3]
        elif up_down < 0:
            up_down = weights[1]
    elif sensor_out == [0, 0, 0] and repeat is True:
        fb = 0

    elif sensor_out == [1, 1, 1]:
        up_down = weights[2]
        fb = 0
    elif sensor_out == [1, 0, 1]:
        up_down = weights[2]

    print(lSpeed, fb, up_down, 0)
    drone.send_rc_control(lSpeed, fb, up_down, 0)


takeoff = False
while True:
    cap = drone.get_frame_read().frame
    img = cv2.resize(cap, (width, height))
    img_to_show = img.copy()

    if takeoff is False:
        takeoff = True
        drone.takeoff()
        time.sleep(1)

    imgThresh = threshold(img, hsv_Vals_red_line)
    markerImage = threshold(img, hsv_Vals_markers)

    sensor_out = getSensorOut(imgThresh, num_sensors)

    marker_width, marker_height = contours(markerImage, img)
    distance_control(marker_height, marker_width, distance_control_minV, distance_control_maxV)
    send_commands(sensor_out)

    # record video
    vid.write_frame(img_to_show)

    cv2.imshow('Img', img)
    # cv2.imshow('Img_thresh', imgThresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

drone.land()
vid.close()
cv2.destroyAllWindows()



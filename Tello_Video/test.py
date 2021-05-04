import cv2
import numpy as np
from djitellopy import tello
import time

me = tello.Tello()
me.connect()
print(me.get_battery())
# me.streamon()
me.takeoff()
time.sleep(3)
#me.send_rc_control(0, 50, 0, 0)
#time.sleep(2)
#me.send_rc_control(0, 0, 0, 0)
me.land()


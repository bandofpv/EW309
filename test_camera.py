# test_camera.py

import time
import threading
from camera import Camera

target_ranges = [304.8, 457.2, 609.6]  # cm
x_bias = [-9.75, -7.59, -15.17]  # cm
y_bias = [-26.08, -46.03, -74.35]  # cm
S_p = [3.41, 5.78, 7.26]  # cm

# Start video stream on seperate thread
# 10 ft: 304.8 15 ft: 457.2 20 ft: 609.6
oakCamera = Camera(457.2, 'orange', target_ranges, x_bias, y_bias, S_p, 30, True)  # start camera instance
camera_thread = threading.Thread(target=oakCamera.stream_video)
camera_thread.start()

while True:
    yaw1, pitch1, yaw2, pitch2 = oakCamera.calc_angles(0, 0)
    print(yaw1, pitch1, yaw2, pitch2)
    num_shots1 = num_shots2 = oakCamera.calc_shots()
    print(num_shots1, num_shots2)
    time.sleep(0.5)

camera_thread.join()
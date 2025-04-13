# test_camera.py

import time
import threading
from camera import Camera

# Start video stream on seperate thread
# 10 ft: 304.8 15 ft: 457.2 20 ft: 609.6
oakCamera = Camera(457.2, 'yellow', 0, 0, 30, True)  # start camera instance
camera_thread = threading.Thread(target=oakCamera.stream_video)
camera_thread.start()

while True:
    time.sleep(0.5)

camera_thread.join()
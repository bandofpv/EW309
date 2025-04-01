import time
import threading
from camera import Camera

# Start video stream on seperate thread
oakCamera = Camera(30, True)  # start camera instance
camera_thread = threading.Thread(target=oakCamera.stream_video)
camera_thread.start()

while True:
    time.sleep(0.5)

camera_thread.join()
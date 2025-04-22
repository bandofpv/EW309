# system_pc.py

import time
import serial
import keyboard
import threading
import numpy as np
import pandas as pd
from camera import Camera
import matplotlib.pyplot as plt

# HARD CODE BIAS CALC
# Bias: If hitting left=make more negative
# Bias: If hitting right=make more positive
# USE Yellow Balls

# 10 ft: 304.8 15 ft: 457.2 20 ft: 609.6
distance_to_target = 388.62  # cm
target_color = 'red'
target_ranges = [304.8, 457.2, 609.6]  # cm
x_bias = [-9.75, -11.59, -15.17]  # cm
y_bias = [-26.08, -45.03, -74.35]  # cm
S_p = [3.41, 5.78, 7.26]  # cm
fps = 30
record = True
sampling_rate = 80  # Hz

ser = serial.Serial('COM21', 9600)  # open serial DATA port

yaw_data = []
pitch_data = []
yaw_velocity_data = []
pitch_velocity_data = []
shot_count_data = []
time_data = []

# Decode serial data
def read_serial(stop_event):
    start_time = time.perf_counter()
    while not stop_event.is_set():
        data = ser.readline().strip().decode("utf-8").split(',')
        yaw_data.append(float(data[0]))
        pitch_data.append(float(data[1]))
        yaw_velocity_data.append(-float(data[2]))
        pitch_velocity_data.append(-float(data[3]))
        shot_count_data.append(data[4])
        time_stamp = time.perf_counter() - start_time
        time_data.append(time_stamp)
        print(f"PICO ({time_stamp}): Yaw: {float(data[0])} Pitch: {data[1]} Yaw Velocity: {data[2]} Pitch Velocity: {data[3]} Shot Count: {data[4]}")

# Start read_serial on seperate thread
stop_event = threading.Event()
serial_thread = threading.Thread(target=read_serial, args=(stop_event,))
serial_thread.start()  # start reading serial port

# Start video stream on seperate thread
oakCamera = Camera(distance_to_target, target_color, target_ranges, x_bias, y_bias, S_p, fps, record)  # start camera instance
camera_thread = threading.Thread(target=oakCamera.stream_video)
camera_thread.start()

# Check if arrow keys are pressed and send serial data to Pico
print("Waiting for keyboard input...")
while True:
    key = keyboard.read_key()
    if keyboard.is_pressed('up'): 
        print('Up arrow pressed')
        ser.write(b"UP\n")  # send to serial 
    elif keyboard.is_pressed('down'):
        print('Down arrow pressed')
        ser.write(b"DOWN\n")  # send to serial 
    elif keyboard.is_pressed('left'):
        print('Left arrow pressed')
        ser.write(b"LEFT\n")  # send to serial 
    elif keyboard.is_pressed('right'):
        print('Right arrow pressed')
        ser.write(b"RIGHT\n")  # send to serial
    elif keyboard.is_pressed('space'):
        print('Space button pressed')
        ser.write(b"SPACE\n")  # send to serial
    elif keyboard.is_pressed('enter'):
        print('Enter button pressed')
        ser.write(b"ENTER\n")  # send to serial
        break
    elif keyboard.is_pressed('q'):
        print('Quitting the program')
        ser.write(b"QUIT\n")  # send to serial
        break
    elif yaw_data:
        oakCamera.snapshot_event.set() # take snapshot
        yaw1, pitch1, yaw2, pitch2 = oakCamera.calc_angles(yaw_data[-1], pitch_data[-1])
        num_shots1 = num_shots2 = oakCamera.calc_shots()
        data_string = f"({yaw1:.3f},{pitch1:.3f},{num_shots1},{yaw2:.3f},{pitch2:.3f},{num_shots2})\n"
        ser.write(data_string.encode('utf-8'))
        print("+++++++SENT+++++++")
        print(yaw1, pitch1, yaw2, pitch2, num_shots1, num_shots2)
        print("==================")
        break

while True:
    if shot_count_data and shot_count_data[-1] >= 10:
        print("Done Shooting")
        break
    time.sleep(1/sampling_rate)  # control loop rate

stop_event.set()  # stop serial_read thread
serial_thread.join()
camera_thread.join()

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_data, yaw_data, marker='.', label='Yaw')
plt.plot(time_data, pitch_data, marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.legend()

# Subplot for Angular Velocity
plt.subplot(2, 1, 2)
plt.plot(time_data, yaw_velocity_data, marker='.', label='Yaw')
plt.plot(time_data, pitch_velocity_data, marker='.', label='Pitch')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend( )
 
# Display plot
plt.tight_layout()
plt.show()

df = pd.DataFrame({'time': time_data, 'yaw': yaw_data, 'pitch': pitch_data, 'yaw_velocity': yaw_velocity_data, 'pitch_velocity': pitch_velocity_data})
df.to_csv("data.csv")
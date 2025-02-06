# manual_IMU_pc.py

import time
import serial
import keyboard
import threading
import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial('COM21', 9600)  # open serial DATA port

sampling_rate = 10  # Hz
yaw_data = []
pitch_data = []
yaw_velocity_data = []
pitch_velocity_data = []

# Read serial data
def read_serial(stop_event):
    # Loop until thread is stopped
    while not stop_event.is_set():
        data = ser.readline().strip().decode("utf-8").split(',')  # decode serial data
        yaw_data.append(float(data[0]))
        pitch_data.append(float(data[1]))
        yaw_velocity_data.append(-float(data[2]))
        pitch_velocity_data.append(-float(data[3]))
        print(f"RECEIVED: Yaw: {float(data[0])} Pitch: {data[1]} Yaw Velocity: {data[2]} Pitch Velocity: {data[3]}")

# Start read_serial on seperate thread
stop_event = threading.Event()
serial_thread = threading.Thread(target=read_serial, args=(stop_event,))
serial_thread.start()

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
    elif keyboard.is_pressed('q'):
        print('Quitting the program')
        ser.write(b"QUIT\n")  # send to serial
        stop_event.set()  # stop serial_read thread
        serial_thread.join()
        break

    time.sleep(1/sampling_rate)  # control loop rate

time_stamps = np.arange(len(yaw_data)) / sampling_rate  # calculate time stamps for plot

# Subplot for Position vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, yaw_data, marker='.', label='Yaw')
plt.plot(time_stamps, pitch_data, marker='.', label='Pitch')
plt.title("Position vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Position (degrees)")
plt.grid(True)
plt.legend()

# Subplot for Angular Velocity
plt.subplot(2, 1, 2)
plt.plot(time_stamps, yaw_velocity_data, marker='.', label='Yaw')
plt.plot(time_stamps, pitch_velocity_data, marker='.', label='Pitch')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend()

# Display plot
plt.tight_layout()
plt.show()
# calc_TF_pc.py

import time
import serial
import keyboard
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ser = serial.Serial('COM21', 9600)  # open serial DATA port

sampling_rate = 100  # Hz
step_duration = 1  # seconds
interval = 1  # seconds between step inputs
yaw_data = []
pitch_data = []
yaw_velocity_data = []
pitch_velocity_data = []

# Decode serial data
def read_serial(stop_event):
    while not stop_event.is_set():
        data = ser.readline().strip().decode("utf-8").split(',')
        yaw_data.append(float(data[0]))
        pitch_data.append(float(data[1]))
        yaw_velocity_data.append(-float(data[2]))
        pitch_velocity_data.append(-float(data[3]))
        print(f"RECEIVED: Yaw: {float(data[0])} Pitch: {data[1]} Yaw Velocity: {data[2]} Pitch Velocity: {data[3]}")

# Start read_serial on seperate thread
stop_event = threading.Event()
serial_thread = threading.Thread(target=read_serial, args=(stop_event,))
# serial_thread.start()

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
        serial_thread.start()  # start reading serial port
        ser.write(b"SPACE\n")  # send initial signal
        time.sleep(2*interval)  # wait for initialization
        ser.write(b"RIGHT\n")  # begin sending step inputs
        time.sleep(step_duration)
        ser.write(b"SPACE\n")
        time.sleep(interval)
        ser.write(b"LEFT\n")
        time.sleep(step_duration)
        ser.write(b"SPACE\n")
        time.sleep(interval)
        ser.write(b"UP\n")
        time.sleep(step_duration)
        ser.write(b"SPACE\n")
        time.sleep(interval)
        ser.write(b"DOWN\n")
        time.sleep(step_duration)
        ser.write(b"SPACE\n")
        time.sleep(2*interval)
        ser.write(b"QUIT\n")
        stop_event.set()  # stop serial_read thread
        serial_thread.join()
        print('Quitting the program')
        break
    elif keyboard.is_pressed('q'):
        print('Quitting the program')
        ser.write(b"QUIT\n")  # send to serial
        stop_event.set()  # stop serial_read thread
        serial_thread.join()
        break

    time.sleep(1/sampling_rate)  # control loop rate

time_stamps = np.arange(len(yaw_data)) / sampling_rate  # calculate time_stamps for plot

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
plt.plot(time_stamps, pitch_velocity_data, marker='.', label='Ptich')
plt.title("Angular Velocity vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Angular Velocity (degrees/sec)")
plt.grid(True)
plt.legend()

# Display plot
plt.tight_layout()
plt.show()

df = pd.DataFrame({'time': time_stamps, 'yaw': yaw_data, 'pitch': pitch_data, 'yaw_velocity': yaw_velocity_data, 'pitch_velocity': pitch_velocity_data})
df.to_csv("data1.csv")
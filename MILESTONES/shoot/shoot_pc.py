# shoot_pc.py

import time
import serial
import keyboard
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ser = serial.Serial('COM21', 9600)  # open serial DATA port

sampling_rate = 60  # Hz
current_data = []
shot_count_data = []
slope_data = []

# Decode serial data
def read_serial(stop_event):
    while not stop_event.is_set():
        data = ser.readline().strip().decode("utf-8").split(',')
        current_data.append(float(data[0]))
        shot_count_data.append(float(data[1]))
        slope_data.append(float(data[2]))
        print(f"RECEIVED: Current: {data[0]} Shot Count: {data[1]} Slope: {data[2]}")

# Start read_serial on seperate thread
stop_event = threading.Event()
serial_thread = threading.Thread(target=read_serial, args=(stop_event,))

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
        time.sleep(1)  # wait for initialization
        ser.write(b"ENTER\n")
        time.sleep(3)
        ser.write(b"QUIT\n")
        stop_event.set()  # stop serial_read thread
        serial_thread.join()
        print('Quitting the program')
        break
    elif keyboard.is_pressed('q'):
        print('Quitting the program')
        ser.write(b"QUIT\n")  # send to serial
        break

    time.sleep(1/sampling_rate)  # control loop rate
    
time_stamps = np.arange(len(current_data)) / sampling_rate  # calculate time_stamps for plot

# Subplot for Slope vs. Time
plt.figure(figsize=(10, 5))
plt.subplot(2, 1, 1)
plt.plot(time_stamps, slope_data, marker='.')
plt.title("Slope vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Slope (amps/sec)")
plt.grid(True)

# Subplot for Shot Count vs. Time
plt.subplot(2, 1, 2)
plt.plot(time_stamps, shot_count_data, marker='.')
plt.title("Shot Count vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Shot Count")
plt.grid(True)

# Display plot
plt.tight_layout()
plt.show()

df = pd.DataFrame({'time': time_stamps, 'current': current_data, 'shot_count': shot_count_data, 'slope': slope_data})
df.to_csv("data.csv")
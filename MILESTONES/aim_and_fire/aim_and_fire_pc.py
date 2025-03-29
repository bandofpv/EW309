# aim_and_fire_pc

import time
import serial
import keyboard
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ser = serial.Serial('COM21', 9600)  # open serial DATA port

sampling_rate = 60  # Hz
yaw_data = []
pitch_data = []
yaw_velocity_data = []
pitch_velocity_data = []
yaw_duty_cycle_data = []
pitch_duty_cycle_data = []
current_data = []
shot_count_data = []
slope_data = []
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
        yaw_duty_cycle_data.append(float(data[4]))
        pitch_duty_cycle_data.append(float(data[5]))
        current_data.append(float(data[6]))
        shot_count_data.append(int(data[7]))
        slope_data.append(float(data[8]))
        time_stamp = time.perf_counter() - start_time
        time_data.append(time_stamp)
        print(f"RECEIVED({time_stamp}): Yaw: {float(data[0])} Pitch: {data[1]} Yaw Velocity: {data[2]} Pitch Velocity: {data[3]} Yaw Duty Cycle: {data[4]} Pitch Duty Cycle: {data[5]} Current: {data[6]} Shot Count: {data[7]} Slope: {data[8]}")

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
        time.sleep(0.1)  # wait for initialization
        ser.write(b"ENTER\n")
        break
    elif keyboard.is_pressed('q'):
        print('Quitting the program')
        ser.write(b"QUIT\n")  # send to serial
        break

    time.sleep(1/sampling_rate)  # control loop rate

while True:
    if shot_count_data and shot_count_data[-1] == 5:
        print("Done Shooting")
        break
    time.sleep(1/sampling_rate)  # control loop rate

stop_event.set()  # stop serial_read thread
serial_thread.join()

plt.figure(figsize=(10, 5))
plt.plot(time_data, current_data, marker='.')
plt.title("Current vs. Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Current (mA)")
plt.grid(True)

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
plt.legend()
 
# Display plot
plt.tight_layout()
plt.show()

df = pd.DataFrame({'time': time_data, 'yaw': yaw_data, 'pitch': pitch_data, 'yaw_velocity': yaw_velocity_data, 'pitch_velocity': pitch_velocity_data, 'yaw_duty_cycle': yaw_duty_cycle_data, 'pitch_duty_cycle': pitch_duty_cycle_data, 'fire_system_current': current_data, 'shot_count': shot_count_data, 'slope': slope_data})
df.to_csv("data1.csv")
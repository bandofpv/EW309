import serial
from pynput import keyboard

ser = serial.Serial('COM19', 9600)  # open serial port

# Check if arrow keys are pressed and send serial data
def on_press(key):
    if key == keyboard.Key.up:
        print('Up arrow pressed')
        ser.write(b"UP!\n") # send to serial 
    elif key == keyboard.Key.down:
        print('Down arrow pressed')
        ser.write(b"DOWN!\n") # send to serial 
    elif key == keyboard.Key.left:
        print('Left arrow pressed')
        ser.write(b"LEFT!\n") # send to serial 
    elif key == keyboard.Key.right:
        print('Right arrow pressed')
        ser.write(b"RIGHT!\n") # send to serial 

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
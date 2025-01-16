import serial

ser = serial.Serial('COM19', 9600)  # open serial port
ser.write(b"Hello I am PC!\n")     # write a string

msg = ser.readline().strip().decode("utf-8").split(',')
print([int(num) for num in msg])
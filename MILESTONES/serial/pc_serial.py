import serial

ser = serial.Serial('COM21', 9600)  # open serial port
# ser.write(b"Hello I am PC!\n")     # write a string
ser.write(b"(10,20,3,-10,0,2)\n")
ser.write(b"\n")

# msg = ser.readline().strip().decode("utf-8").split(',')
# print(msg)
# print([float(num) for num in msg])
import ttyacm
tty = ttyacm.open(1)

print("Reading data from DATA")
msg = tty.readline()
print(msg)

print("Sending data to DATA")
tty.print("100,8")
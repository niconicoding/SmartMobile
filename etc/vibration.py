import serial
from time import sleep

while True:
    bluetoothSerial = serial.Serial("/dev/rfcomm0", baudrate=9600)
    bluetoothSerial.write(("w").encode('utf-8'))
    sleep(1)

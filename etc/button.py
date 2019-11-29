import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN)

while True:
    if GPIO.input(18) == 0:
        print("button!")
        #time.sleep(0.5)

from gpiozero import Buzzer

buzzer = Buzzer(3)

while True :
	buzzer.on()


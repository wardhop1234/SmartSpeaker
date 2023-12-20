import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

print("started")

while True:
    print("on")
    GPIO.output(25,True)
    GPIO.output(23,True)
    GPIO.output(27,True)
    time.sleep(1)
    print("off")
    GPIO.output(25,False)
    GPIO.output(23,False)
    GPIO.output(27,False)
    time.sleep(1)
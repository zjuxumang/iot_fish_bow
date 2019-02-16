import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(8,GPIO.OUT)
p = GPIO.PWM(8,50)
p.start(0)
time.sleep(1)
try:
    while 1:
        p.ChangeDutyCycle(5)
        time.sleep(1)
        p.ChangeDutyCycle(0)
        time.sleep(2)
        p.ChangeDutyCycle(10)
        time.sleep(1)
        p.ChangeDutyCycle(0)
        time.sleep(2)
except KeyboardInterrupt:
        pass
p.stop()
GPIO.cleanup()

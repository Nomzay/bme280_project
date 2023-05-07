#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
# die GPIOS koennen über die PINNummer oder die GPIONummer
# angesprochen werden
GPIO.setmode(GPIO.BCM) # hier GPIO-Nummer
GPIO.setup(18, GPIO.OUT)
 
interval_in_s = 5.0
while(True):
	print("off")
	GPIO.output(18, GPIO.HIGH)
	time.sleep(interval_in_s) # sleep interval in sec
	print("on")
	GPIO.output(18, GPIO.LOW)
	time.sleep(interval_in_s)

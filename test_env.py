#!/usr/bin/env python3

import time
import board
import datetime
from adafruit_bme280 import basic as adafruit_bme280
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient

# functions
def write_to_influx( client , temp , humi , threshold , timpstemp ):
  data = [
      {
          "measurement": "bme280",
          "time": timestamp,
          "fields": {
              "temperature": temp,
              "humidity": humi,
              "threshold_temperature": threshold   
          }
      }
  ]
  client.write_points(data)

# settings for influxdb
host     = "localhost"
port     = "8086"
username = "admin"
password = "jgoeckem"
dbname   = "serverroom_temp"

# setting up GPIO via I2C
GPIO_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup( GPIO_PIN , GPIO.OUT)

i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# connecting to influxdb
client = InfluxDBClient(host,port,username,password,dbname)


TEMP_THRESHOLD = 20.0
bme280.sea_level_pressure = 1013.25

# main loop
while True:
  
  temperature = bme280.temperature
  humidity    = bme280.humidity
  pressure    = bme280.pressure
  timestamp   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  altitude    = bme280.altitude
  print(f'Time: {timestamp} | Temp: {temperature} | Pressure: {pressure} | Humidity: {humidity} | Altitude: {altitude}')

  #write_to_influx( client, temperature , humidity , TEMP_THRESHOLD , timestamp )
  
  if temperature <= TEMP_THRESHOLD:
    GPIO.output(GPIO_PIN, GPIO.HIGH)
  
  else:
    GPIO.output(GPIO_PIN, GPIO.LOW)
    
  time.sleep(10)
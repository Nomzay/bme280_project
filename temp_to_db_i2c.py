#!/usr/bin/env python3

# ---------------------------------------- H E A D E R ---------------------------------------- #
#
# TITLE: BME280 supported evaluation program
# AUTHOR: Goeckemeyer Jasmon, Deutzmann Nick, Wolbeck Lukas, Karagöz Abdullah, Simon Matthias
# VERSION: 1.3 
#
# ---------------------------------------- L I B R A R I E S ---------------------------------- #

import time
import datetime
import math

import csv
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient

# ---------------------------------------- F U N C T I O N S ---------------------------------- #

def write_to_influx( client , temp , fahr , press , humi , dew , threshold , timpstamp ):
  data = [
      {
          "measurement": "bme280",
          "time": timestamp,
          "fields": {
              "temperature": temp,
              "fahrenheit": fahr,
              "pressure": press,
              "humidity": humi,
              "dewpoint": dew,
              "threshold_temperature": threshold   
          }
      }
  ]
  client.write_points(data)
  
def read_file_to_float( path_to_file ):
  f = open(path_to_file)
  value = f.read()
  value = float( value.replace("\n","") )
  return value
  
def dew_point( temperature , humidity ):
  a = 17.27
  b = 237.7
  alpha = ( ( a * temperature ) / ( b + temperature ) ) + math.log( humidity / 100.0 )
  return round( (b * alpha) / (a - alpha) , 2 )
  
def write_to_csv( temp , fahr , press , humi , dew , timestamp





# ---------------------------------------- M A I N -------------------------------------------- #
def main():

  # settings for influxdb
  host     = "localhost"
  port     = "8086"
  username = "admin"
  password = "jgoeckem"
  dbname   = "serverroom_temp"

  # setting up GPIO
  GPIO_PIN = 18
  GPIO.setmode(GPIO.BCM)
  GPIO.setwarnings(False)
  GPIO.setup( GPIO_PIN , GPIO.OUT)


  # connecting to influxdb
  client = InfluxDBClient(host,port,username,password,dbname)
  
  # final variables
  TEMP_THRESHOLD = 20.0
  SLEEP_TIMER = 20
  SWITCH_INTERVAL = 6

  DEVICE_FILE_LOCATION = "/sys/bus/iio/devices/iio:device0/"
  TEMPERATURE_FILE     = "in_temp_input"
  HUMIDITY_FILE        = "in_humidityrelative_input"
  PRESSURE_FILE        = "in_pressure_input"
  
  while True:

    counter = 1
    avg_temp = 0.0
  
    while  counter <= SWITCH_INTERVAL:
  
      temperature = round( read_file_to_float( DEVICE_LOCATION + TEMPERATURE_FILE_LOCATION ) , 2 )
      humidity    = int( read_file_to_float( DEVICE_LOCATION + HUMIDITY_FILE_LOCATION ) )
      pressure    = int( read_file_to_float( DEVICE_LOCATION + PRESSURE_FILE_LOCATION ) * 10)
    
      dewpoint    = dew_point( temperature , humidity )
      fahrenheit  = round( temperature * 1.8 + 32 , 2 )
      timestamp   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      write_to_influx( client , temperature , fahrenheit , pressure , humidity , dewpoint , TEMP_THRESHOLD , timestamp )
    
      avg_temp += temperature
      counter += 1
    
      time.sleep( SLEEP_TIMER )
  
    avg_temp /= (counter - 1)
  
    if avg_temp <= TEMP_THRESHOLD:
      GPIO.output(GPIO_PIN, GPIO.HIGH)
  
    else:
      GPIO.output(GPIO_PIN, GPIO.LOW)
    
# ---------------------------------------- S T A R T ----------------------------------------- #

if __name__ == "__main__":
  main() 
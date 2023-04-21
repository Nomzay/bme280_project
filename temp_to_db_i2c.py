#!/usr/bin/env python3

# ---------------------------------------- H E A D E R ---------------------------------------- #
#
# TITLE: BME280 supported evaluation program
# AUTHOR: Goeckemeyer Jasmon, Deutzmann Nick, Wolbeck Lukas, Karagoez Abdullah, Simon Matthias
# VERSION: 1.4 
#
# ---------------------------------------- L I B R A R I E S ---------------------------------- #

import time
import datetime
import math

import csv
import RPi.GPIO as GPIO
from influxdb import InfluxDBClient

# ---------------------------------------- F U N C T I O N S ---------------------------------- #

# function writes data to influxdb
def write_to_influx( client , temp , fahr , press , humi , dew , threshold , timestamp ):
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

# function writes data to csv file
def write_to_csv( temp , fahr , press , humi , dew , timestamp , writer ):
  data = [ timestamp , temp , fahr , press , humi , dew ]
  writer.writerow( data )
  
def write_to_console( time , temp , fahr , press , humi , dew ):
  print(f'##########################################\n' +
  f'TIMESTAMP:      {time}\n'  +
  f'TEMPERATURE:    {temp} CELSIUS\n'  +
  f'FAHRENHEIT:     {fahr} FAHRENHEIT\n'  +
  f'PRESSURE:       {press} HEKTOPASCAL\n' +
  f'HUMIDITY:       {humi} PERCENT\n'  +
  f'DEWPOINT:       {dew} CELSIUS\n')

# function reads data from specified file path
def read_file_to_float( path_to_file ):
  f = open(path_to_file)
  value = f.read()
  value = float( value.replace("\n","") )
  return value

# function calulates dew point with given temperature and humidity
def dew_point( temperature , humidity ):
  a = 17.27
  b = 237.7
  alpha = ( ( a * temperature ) / ( b + temperature ) ) + math.log( humidity / 100.0 )
  return round( (b * alpha) / (a - alpha) , 2 )
  
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
  TEMP_THRESHOLD  = 20.0
  SLEEP_TIMER     = 20
  SWITCH_INTERVAL = 6

  DEVICE_LOCATION      = "/sys/bus/iio/devices/iio:device0/"
  TEMPERATURE_FILE     = "in_temp_input"
  HUMIDITY_FILE        = "in_humidityrelative_input"
  PRESSURE_FILE        = "in_pressure_input"
  
  
  CSV_FIELDNAMES = ['TIMESTAMP','TEMPERATURE','FAHRENHEIT','PRESSURE','HUMIDITY','DEW_POINT']
  PATH_TO_CSV    = "/home/jgoeckem/bme280_project/bme_logs/"
  CSV_FILENAME   = PATH_TO_CSV + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '_DATA_LOG.csv'
  
  
  csv_file  = open( CSV_FILENAME , 'w' )
  writer    = csv.writer( csv_file )
  
  writer.writerow( CSV_FIELDNAMES )
  while True:

    counter = 1
    avg_temp = 0.0
  
    while  counter <= SWITCH_INTERVAL:
  
      temperature = round( read_file_to_float( DEVICE_LOCATION + TEMPERATURE_FILE ) / 1000 , 2 )
      humidity    = int( read_file_to_float( DEVICE_LOCATION + HUMIDITY_FILE ) / 1000 )
      pressure    = int( read_file_to_float( DEVICE_LOCATION + PRESSURE_FILE ) * 10 )
    
      dewpoint    = dew_point( temperature , humidity )
      fahrenheit  = round( temperature * 1.8 + 32 , 2 )
      timestamp   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      #write_to_influx( client , temperature , fahrenheit , pressure , humidity , dewpoint , TEMP_THRESHOLD , timestamp )
      
      write_to_csv( temperature , fahrenheit , pressure , humidity , dewpoint , timestamp , writer )
      
      write_to_console ( timestamp , temperature , fahrenheit , pressure , humidity , dewpoint )
      
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
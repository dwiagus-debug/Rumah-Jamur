import BlynkLib
from BlynkTimer import BlynkTimer

import Adafruit_DHT
import sys
import RPi.GPIO as GPIO
import time
import datetime

sys.path.append('/home/dwiagus/lcd-library')
import drivers

display = drivers.Lcd()

GPIO.setmode(GPIO.BCM)
RELAY1_PIN = 17
RELAY2_PIN = 27
GPIO.setup(RELAY1_PIN, GPIO.OUT)
GPIO.setup(RELAY2_PIN, GPIO.OUT)
GPIO.output(RELAY1_PIN, GPIO.HIGH)
GPIO.output(RELAY2_PIN, GPIO.HIGH)

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
BLYNK_AUTH_TOKEN = 'x8sCM9NEpJEer6gtD3pmWiT-w89j-Tc5'

# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH_TOKEN)

# Create BlynkTimer Instance
timer = BlynkTimer()


# function to sync the data from virtual pins
@blynk.on("connected")
def blynk_connected():
	print("Welcome to Mushroom Monitoring System")
	print(".......................................................")
	print("..................... By Dwi Agus .....................")
	display.lcd_display_string("Mushroom Monitor", 1)
	display.lcd_display_string("By Dwi Agus", 2)
	time.sleep(2);

# Functon for collect data from sensor & send it to Server
def myData():
	pump_status = "Off"
	fan_status = "Off"

	file_exists = os.path.isfile('data_logger.txt')
	file = open('data_logger.txt', 'a')

	if not file_exists:
    	file.write('Time and Date, temperature (ºC), humidity (%)\n')


	humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
	display.lcd_clear()
	if humidity is not None and temperature is not None:
		display.lcd_display_string("T:" + str(temperature) + ", H:" + str(humidity), 1)
		print("Temperature = " + str(temperature) + ", Humidity " + str(humidity))
	else:
		print("Sensor failure. Check wiring.");

	if temperature >= 28.00 and temperature <= 40.00:
		GPIO.output(RELAY1_PIN, GPIO.LOW)
		GPIO.output(RELAY2_PIN, GPIO.LOW)
		print("Pump and Fan On")
		pump_status = "On"
		fan_status = "On"
	else:
		GPIO.output(RELAY1_PIN, GPIO.HIGH)
		GPIO.output(RELAY2_PIN, GPIO.HIGH)
		print("Pump and Fan Off")
		pump_status = "Off"
		fan_status = "Off"

	datetime = datetime.datetime.now()
    file.write(datetime + ', {:.2f}, {:.2f}\n'.format(temperature, humidity))

	display.lcd_display_string("Pump:" + pump_status + ",Fan:" + fan_status, 2)

	blynk.virtual_write(0, humidity)
	blynk.virtual_write(1, temperature)
	blynk.virtual_write(2, pump_status)
	blynk.virtual_write(3, fan_status)
	print("Data sensor DHT11 sent to New Blynk Server!")
	time.sleep(2);

timer.set_interval(2, myData)


while True:
	blynk.run()
	timer.run()

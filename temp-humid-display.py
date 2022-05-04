# Take sensor reading
# and display it using 4 x LED 7 segments displays (multiplexed)
# Requirements:
#   pip3 install --user python-periphery
# Run at boot:
# /etc/rc.local:
#    su -c 'python /home/pi/Development/rpi-gpio-experiments/temp-humid-display.py > /home/pi/sensor.log 2>&1' pi &

from periphery import I2C
import time
import sys
import RPi.GPIO as gpio

# I2C sensor related
SENSOR_ADDRESS = 0x27

VALID_DATA = 0
STALE_DATA = 1

bus = I2C("/dev/i2c-1")

# Display related
A = 11
B = 8
C = 10
D = 12

# Digits selectors must be set HIGH when inactive
DIGIT1 = 15
DIGIT2 = 16
DIGIT3 = 18
DIGIT4 = 19

TEMP = 10
HUMID = 11
OFF = 15

REFRESH_WAIT = 3 / 1000

digits = (DIGIT1, DIGIT2, DIGIT3, DIGIT4)
bin_decoder = (A, B, C, D)
outputs = (A, B, C, D, DIGIT1, DIGIT2, DIGIT3, DIGIT4)

gpio.setmode(gpio.BOARD)
gpio.setup(outputs, gpio.OUT)

last_selected_digit = None
temp_readings = []
humidity_readings = []

def sensor_reading():
    '''Send a measurement request and a read request
    to the sensor'''

    # measurement request
    measure_msg = I2C.Message([])
    bus.transfer(SENSOR_ADDRESS, [measure_msg])
    time.sleep(.05)
    # read the measurement
    read_msg = I2C.Message([0x0, 0x0, 0x0, 0x0], read = True)
    bus.transfer(SENSOR_ADDRESS, [read_msg])
    raw_data = read_msg.data

    # first 2 bits represent the response status
    reading_status = raw_data[0] >> 6
    if reading_status != VALID_DATA and reading_status != STALE_DATA:
        print('Invalid data:', reading_status, raw_data, file=sys.stderr)
        return (None, None)

    # next 14 bits represent the humidity value
    humidity = ((raw_data[0] & 0x3f) << 8) | raw_data[1]
    humidity = humidity / (2 ** 14 - 2) * 100

    # next 14 bits represent the temperature
    temp = (raw_data[2] << 6) | raw_data[3]
    temp = (temp / (2 ** 14 - 2) * 165 - 40) - 2
    temp_readings.append(temp)
    humidity_readings.append(humidity)

    if len(temp_readings) > 10:
        temp_readings.pop(0)
        humidity_readings.pop(0)

    if len(temp_readings) == 10:
        temp = sum(temp_readings) / len(temp_readings)
        humidity = sum(humidity_readings) / len(humidity_readings)

    return (humidity, temp)

def init_display():
    # Digits selectors should be set HIGH
    reset_digits()

    # Turn off all digits
    display_digit(OFF)

def reset_digits():
    gpio.output(DIGIT1, 1)
    gpio.output(DIGIT2, 1)
    gpio.output(DIGIT3, 1)
    gpio.output(DIGIT4, 1)

def turnoff_digits():
    if last_selected_digit is not None:
        gpio.output(last_selected_digit, 1)

def select_digit(digit):
    global last_selected_digit

    if last_selected_digit is not None:
        gpio.output(last_selected_digit, 1)

    gpio.output(digit, 0)
    last_selected_digit = digit

def display_digit(number):
    for i in range(4):
        gpio.output(bin_decoder[i], bit(number, i))

def display_value(number, indicator, timeout = 3):
    float_str = str(float(number))
    whole, dec = float_str.split('.', 1)

    text = whole[-2:] + dec[0]
    now = time.time()

    while True:
        digit = 0

        if (time.time() - now) > timeout:
            break
        for c in text:
            turnoff_digits()
            display_digit(int(c))
            select_digit(digits[digit])
            time.sleep(REFRESH_WAIT)

            digit += 1

            if digit > 2:
                break

        turnoff_digits()
        display_digit(indicator)
        select_digit(digits[digit])
        time.sleep(REFRESH_WAIT)

def bit(value, bit_index):
    return (value >> bit_index) & 1

try:
    # init_display()

    while True:
        humidity, temp = sensor_reading()
        if humidity is None or temp is None:
            time.sleep(1)
            continue

        # Print a number
        print(temp, humidity)
        display_value(temp, TEMP)
        display_value(humidity, HUMID)

finally:
    gpio.cleanup()


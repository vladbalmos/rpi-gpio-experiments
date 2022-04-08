# Honeywell HIH800 series humidity & temperature sensor reading
# using i2c through python-periphery on a Raspberry PI

from periphery import I2C
import sys
import time

SENSOR_ADDRESS = 0x27

VALID_DATA = 0
STALE_DATA = 1

bus = I2C("/dev/i2c-1")

def sensor_reading():
    '''Send a measurement request and a read request
    to the sensor'''

    # measurement request
    measure_msg = I2C.Message([])
    bus.transfer(SENSOR_ADDRESS, [measure_msg])
    time.sleep(.1)
    # read the measurement
    read_msg = I2C.Message([0x0, 0x0, 0x0, 0x0], read = True)
    bus.transfer(SENSOR_ADDRESS, [read_msg])
    raw_data = read_msg.data

    # first 2 bits represent the response status
    reading_status = raw_data[0] >> 6
    if reading_status != VALID_DATA and reading_status != STALE_DATA:
        print('Invalid data:', status, file=sys.stderr)
        return (None, None)

    # next 14 bits represent the humidity value
    humidity = ((raw_data[0] & 0x3f) << 8) | raw_data[1]
    humidity = humidity / (2 ** 14 - 2) * 100

    # next 14 bits represent the temperature
    temp = (raw_data[2] << 6) | raw_data[3]
    temp = temp / (2 ** 14 - 2) * 165 - 40

    return (humidity, temp)


while True:
    data = sensor_reading()
    print(data)
    time.sleep(1)

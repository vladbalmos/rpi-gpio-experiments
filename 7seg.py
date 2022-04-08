# 7 segment display counter driver
import time
import RPi.GPIO as gpio

def bit(value, bit_index):
    return (value >> bit_index) & 1

outputs = (11, 12, 19, 21)

gpio.setmode(gpio.BOARD)
gpio.setup(outputs, gpio.OUT)

def run():
    counter = 0
    while True:
        print(counter)
        for i in range(4):
            gpio.output(outputs[i], bit(counter, i))

        time.sleep(1)

        counter += 1

        if counter > 15:
            counter = 0

try:
    run()
finally:
    gpio.cleanup()


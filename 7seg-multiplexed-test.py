# 7 segment display counter driver
import time
import sys
import RPi.GPIO as gpio

def bit(value, bit_index):
    return (value >> bit_index) & 1

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
HUMID = 12

DIGIT_WAIT = 3 / 1000

digits = (DIGIT1, DIGIT2, DIGIT3, DIGIT4)
bin_decoder = (A, B, C, D)
outputs = (A, B, C, D, DIGIT1, DIGIT2, DIGIT3, DIGIT4)

gpio.setmode(gpio.BOARD)
gpio.setup(outputs, gpio.OUT)

wait = 0.1
last_selected_digit = None

def select_digit(digit):
    global last_selected_digit

    if last_selected_digit is not None:
        gpio.output(last_selected_digit, 1)

    gpio.output(digit, 0)
    last_selected_digit = digit

def turnoff_digits():
    if last_selected_digit is not None:
        gpio.output(last_selected_digit, 1)

def display_digit(number):
    for i in range(4):
        gpio.output(bin_decoder[i], bit(number, i))

def reset_digits():
    gpio.output(DIGIT1, 1)
    gpio.output(DIGIT2, 1)
    gpio.output(DIGIT3, 1)
    gpio.output(DIGIT4, 1)



def setup():
    # Digits selectors should be set HIGH
    reset_digits()

    # Turn off all digits
    display_digit(15)

def digit_test(digit_index, number):
    digit = digits[digit_index]
    select_digit(digit)
    display_digit(number)
    time.sleep(wait)
    for number in range(10):
        display_digit(number)
        time.sleep(wait)


def display_number(number, indicator):
    float_str = str(float(number))
    whole, dec = float_str.split('.', 1)

    text = whole[-2:] + dec[0]
    now = time.time()

    while True:
        digit = 0

        if (time.time() - now) > 3:
            break
        for c in text:
            turnoff_digits()
            display_digit(int(c))
            select_digit(digits[digit])
            time.sleep(DIGIT_WAIT)

            digit += 1

            if digit > 2:
                break

        turnoff_digits()
        display_digit(indicator)
        select_digit(digits[digit])
        time.sleep(DIGIT_WAIT)


try:
    setup()

    while True:
        # Cycle all digits
        for counter in range(4):
            digit_test(counter, counter)

        # Print a number
        display_number(20.3, TEMP)
        display_number(33.9, HUMID)

finally:
    gpio.cleanup()


#! /usr/bin/python3

import pigpio
import time

# This script enables SPI as well as doing things with pins to make the motor
# turn. It is intended to be as simple as possible, and just make the thing go
# forward and backward.

#######################################
# Set pin numbers                     #
# Change according to your own wiring #
#######################################

# Motor 1
m1_a1 = 17 # SPI1 CE1
m1_a2 = 23
m1_b1 = 24
m1_b2 = 25
m1_pins = (m1_a1, m1_a2, m1_b1, m1_b2)

# Motor 2
m2_a1 = 22 
m2_a2 = 18
m2_b1 = 8 # SPI0 CE0
m2_b2 = 9
m2_pins = (m2_a1, m2_a2, m2_b1, m2_b2)

# Limit switches
# x and y refer to the driver (x-drive side/y-drive side)
limit_y_end = 4
limit_x_end = 5
limit_y_move = 6
limit_x_move = 12
limit_pins = (limit_y_end, limit_x_end, limit_y_move, limit_x_move)

# Laser module
laser_pin = 27

# start daemon, and connect
def start_pigpiod():
    pi = pigpio.pi()
    if not pi.connected:
        raise "pigpio daemon could not connect"
    else:
        return pi
# end start_pigpiod

pi = start_pigpiod()
    
# OPTPUT pins
pi.set_mode(m1_a1, pigpio.OUTPUT)
pi.set_mode(m1_a2, pigpio.OUTPUT)
pi.set_mode(m1_b1, pigpio.OUTPUT)
pi.set_mode(m1_b2, pigpio.OUTPUT)
pi.set_mode(m2_a1, pigpio.OUTPUT)
pi.set_mode(m2_a2, pigpio.OUTPUT)
pi.set_mode(m2_b1, pigpio.OUTPUT)
pi.set_mode(m2_b2, pigpio.OUTPUT)
pi.set_mode(laser_pin, pigpio.OUTPUT)

# INPUT pins (and set the PUD resistor)
pi.set_mode(limit_y_end, pigpio.INPUT)
pi.set_pull_up_down(limit_y_end, pigpio.PUD_UP)
pi.set_mode(limit_x_end, pigpio.INPUT)
pi.set_pull_up_down(limit_x_end, pigpio.PUD_UP)
pi.set_mode(limit_y_move, pigpio.INPUT)
pi.set_pull_up_down(limit_y_move, pigpio.PUD_UP)
pi.set_mode(limit_x_move, pigpio.INPUT)
pi.set_pull_up_down(limit_x_move, pigpio.PUD_UP)

# open SPI at 50k bps in mode 2
# TODO: Figure out the modes!!!
# http://abyz.me.uk/rpi/pigpio/python.html#spi_open
pi.spi_open(m2_b1, 50000, 2)
pi.spi_open(m1_a1, 50000, 2)


#######################################
#  Main Processing Code               #
#######################################

# Define the on/off positions for motor movement
number_steps = 8
seq = range(0, number_steps)
seq[0] = [0,1,0,0]
seq[1] = [0,1,0,1]
seq[2] = [0,0,0,1]
seq[3] = [1,0,0,1]
seq[4] = [1,0,0,0]
seq[5] = [1,0,1,0]
seq[6] = [0,0,1,0]
seq[7] = [0,1,1,0]

all_off = [0,0,0,0]

# Takes a list of pins, and the desired on/off pattern
def set_step(motor_pins, step_sequence):
    counter = 0
    for pin in motor_pins:
        GPIO.output(pin, step_sequence[counter])
        counter++

# Loops forward through the motor sequence
def forward(motor, steps, delay):
    for i in range(steps):
        if GPIO.event_detected(limit_pins):
            break
        for j in range(number_steps):
            set_step(motor, seq[j])
            time.sleep(delay)
    set_step(motor, all_off)

# Loops backward through the motor sequence
def backward(motor, steps, delay):
    for i in range(steps):
        if GPIO.event_detected(limit_pins):
            break
        for j in reversed(range(number_steps)):
            set_step(motor, seq[j])
            time.sleep(delay)
    set_step(motor, all_off)

if __name__ == '__main__':
    carry_on = True
    while carry_on:
        delay = input("Time between micro-steps (ms)? ")
        steps = input("Number of full steps forward? ")
        forward(motor1_pins, int(steps), int(delay) / 1000.0)
        steps = input("Number of full steps backward? ")
        backward(motor1_pins, int(steps), int(delay) / 1000.0)
        keep_going = input("Run again? ")
        carry_on = keep_going.capitalize() == 'Yes' or keep_going.capitalize() == 'True'

    # At the end of it all, clean up
    pi.stop()

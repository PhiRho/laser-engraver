#! /usr/bin/python3

import RPi.GPIO as GPIO
import time

# This is a basic script which should turn the motors on and off.
# It should set the GPIO pins for the various modules, and engage listeners for 
# the limit switches so they can short circuit the motors.

#######################################
#  Set pin numbers                    #
#######################################

# Motor 1
m1_a1 = 22
m1_a2 = 23
m1_b1 = 24
m1_b2 = 25
m1_pins = (m1_a1, m1_a2, m1_b1, m1_b2)

# Motor 2
m2_a1 = 17
m2_a2 = 18
m2_b1 = 10
m2_b2 = 9
m2_pins = (m2_a1, m2_a2, m2_b1, m2_b2)

# Limit switches
# x and y refer to the driver (x-drive side/y-drive side)
limit_y_end = 4
limit_x_end = 0
limit_y_move = 0
limit_x_move = 0
limit_pins = (limit_y_end, limit_x_end, limit_y_move, limit_x_move)

# Laser module
laser_pin = 0

# GPIO Setup

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Output pins
GPIO.setup(m1_a1, GPIO.OUT)
GPIO.setup(m1_a2, GPIO.OUT)
GPIO.setup(m1_b1, GPIO.OUT)
GPIO.setup(m1_b2, GPIO.OUT)
GPIO.setup(m2_a1, GPIO.OUT)
GPIO.setup(m2_a2, GPIO.OUT)
GPIO.setup(m2_b1, GPIO.OUT)
GPIO.setup(m2_b2, GPIO.OUT)
GPIO.setup(laser_pin, GPIO.OUT)

# Input pins
GPIO.setup(limit_y_end, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(limit_x_end, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(limit_y_move, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(limit_x_move, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Default outputs to OFF
GPIO.output(m1_pins, GPIO.LOW)
GPIO.output(m2_pins, GPIO.LOW)
GPIO.output(laser_pin, GPIO.LOW)

# Set up events on inputs
GPIO.add_event_detect(limit_pins, GPIO.BOTH)

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
    GPIO.output(motor_pins, step_sequence)

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
    GPIO.cleanup()

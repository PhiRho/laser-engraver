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

__init__():
    pi = # connect to pigpiod
    
    pi.set_mode(m1_a1, pigpio.OUTPUT)
    pi.set_mode(m1_a2, pigpio.OUTPUT)
    pi.set_mode(m1_b1, pigpio.OUTPUT)
    pi.set_mode(m1_b2, pigpio.OUTPUT)
    pi.set_mode(m2_a1, pigpio.OUTPUT)
    pi.set_mode(m2_a2, pigpio.OUTPUT)
    pi.set_mode(m2_b1, pigpio.OUTPUT)
    pi.set_mode(m2_b2, pigpio.OUTPUT)
    pi.set_mode(laser_pin, pigpio.OUTPUT)

    pi.set_mode(limit_y_end, pigpio.INPUT)
    pi.set_pull_up_down(limit_y_end, pigpio.PUD_UP)
    pi.set_mode(limit_x_end, pigpio.INPUT)
    pi.set_pull_up_down(limit_x_end, pigpio.PUD_UP)
    pi.set_mode(limit_y_move, pigpio.INPUT)
    pi.set_pull_up_down(limit_y_move, pigpio.PUD_UP)
    pi.set_mode(limit_x_move, pigpio.INPUT)
    pi.set_pull_up_down(limit_x_move, pigpio.PUD_UP)

# end __init__


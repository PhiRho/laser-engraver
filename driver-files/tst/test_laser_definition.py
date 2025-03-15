import pytest
from src.laser_definition import Laser
from src.mock_pi import MockPi
from src.motor_definition import Motor

# Important to note, all of these pin numbers are dummies. DO NOT USE THEM ON A REAL PI.
pi = MockPi()
x_motor = Motor(1, 2, 3, 4, 5, pi)
y_motor = Motor(6, 7, 8, 9, 10, pi)
x_limits = (11, 12)
y_limits = (13, 14)
laser_pin = 15

def test_laser_definition_init():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.pi == pi

def test_step_count_from_distance():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.step_count_from_distance(10) == 50
    assert laser.step_count_from_distance(0.5) == 2

def test_step_delay_from_speed():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.step_delay_from_speed(20) == 10 / 1000.0

def test_move_x():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    laser.move_x(1, 1, Motor.Direction.CLOCKWISE)
    assert laser.location[0] == -1
    laser.move_x(1, 1, Motor.Direction.COUNTERCLOCKWISE)
    assert laser.location[0] <= 0.0001

def test_interrupt_movement():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    x_pos = laser.location[0]
    laser.interrupt_movement(x_limits[1], 1, 0)
    assert laser.stop_motor == True
    assert round(laser.location[0]) == x_pos - 10

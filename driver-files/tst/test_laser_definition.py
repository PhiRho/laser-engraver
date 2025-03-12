import pytest
from src.laser_definition import LaserDefinition
from tst.mock_pi import MockPi
from src.motor_definition import Motor

# Important to note, all of these pin numbers are dummies. DO NOT USE THEM ON A REAL PI.
pi = MockPi()
x_motor = Motor(1, 2, 3, 4, 5, pi)
y_motor = Motor(6, 7, 8, 9, 10, pi)
x_limits = (11, 12)
y_limits = (13, 14)
laser_pin = 15

def test_laser_definition_init():
    laser_definition = LaserDefinition(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser_definition.pi == pi

def test_step_count_from_distance():
    laser_definition = LaserDefinition(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser_definition.step_count_from_distance(10) == 50
    assert laser_definition.step_count_from_distance(0.5) == 2

def test_step_delay_from_speed():
    laser_definition = LaserDefinition(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser_definition.step_delay_from_speed(20) == 10 / 1000.0




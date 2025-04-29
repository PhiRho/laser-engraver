import pytest
import time
from src.motor_definition import Motor
from src.mock_pi import MockPi

pi = MockPi()

def test_motor_init():
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step == 1
    assert motor.direction == 2
    assert motor.ms1 == 3
    assert motor.ms2 == 4
    assert motor.ms3 == 5

"""Smoke test. Should not raise exceptions"""
def test_step_with_delay():
    motor = Motor(1, 2, 3, 4, 5, pi)
    motor.step_with_delay(0.001)

def test_set_microstep():
    motor = Motor(1, 2, 3, 4, 5, pi)
    motor.set_microstep(1)
    assert pi.read(motor.ms1) == 0
    assert pi.read(motor.ms2) == 0
    assert pi.read(motor.ms3) == 0

    motor.set_microstep(2)
    assert pi.read(motor.ms1) == 1
    assert pi.read(motor.ms2) == 0
    assert pi.read(motor.ms3) == 0
    
def test_set_direction():
    motor = Motor(1, 2, 3, 4, 5, pi)
    motor.set_direction(Motor.Direction.CLOCKWISE)
    assert pi.read(motor.direction) == 0
    motor.set_direction(Motor.Direction.COUNTERCLOCKWISE)
    assert pi.read(motor.direction) == 1

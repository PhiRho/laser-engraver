import pytest
from laser_definition import Motor
import pigpio
import logging

logging.basicConfig(level=logging.DEBUG)

class MockPi(pigpio.pi):
    def __init__(self):
        super().__init__()

    def write(self, gpio, value):
        print("write", gpio, value)
        pass

    def set_mode(self, gpio, mode):
        print("set_mode", gpio, mode)
        pass

    def gpio_trigger(self, gpio, level, delay):
        pass

pi = MockPi()

def test_motor_init():
    """Test that Motor initializes with correct pin assignments"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step == 1
    assert motor.direction == 2
    assert motor.ms1 == 3
    assert motor.ms2 == 4
    assert motor.ms3 == 5

def test_motor_move():
    """Test motor move method"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    motor.move(0.5, 20)  # Basic smoke test - should not raise exception

def test_motor_speed_too_slow():
    """Test that motor raises an exception if the speed is too slow"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(1, 1)

def test_motor_speed_too_fast():
    """Test that motor raises an exception if the speed is too fast"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(1, 1000)

def test_step_count_from_distance():
    """Test that step_count_from_distance returns the correct number of steps"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step_count_from_distance(10) == 50
    assert motor.step_count_from_distance(0.5) == 2

def test_step_delay_from_speed():
    """Test that step_delay_from_speed returns the correct delay"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step_delay_from_speed(20) == 10 / 1000.0

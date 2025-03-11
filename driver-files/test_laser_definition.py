import pytest
from laser_definition import Motor
import pigpio

class MockPi(pigpio.pi):
    def __init__(self):
        super().__init__()

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
    motor.move(10, 10)  # Basic smoke test - should not raise exception

def test_motor_speed_too_slow():
    """Test that motor raises an exception if the speed is too slow"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(10, 0.000001)

def test_motor_speed_too_fast():
    """Test that motor raises an exception if the speed is too fast"""
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(10, 1000000)

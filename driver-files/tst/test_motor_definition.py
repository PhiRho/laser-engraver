import pytest
from src.motor_definition import Motor
import pigpio
import logging

logging.basicConfig(level=logging.DEBUG)

class MockPi(pigpio.pi):
    assigned_gpio_values = {}

    def __init__(self):
        super().__init__()

    def write(self, gpio, value):
        print("write", gpio, value)
        self.assigned_gpio_values[gpio] = value

    def set_mode(self, gpio, mode):
        print("set_mode", gpio, mode)
        self.assigned_gpio_values[gpio] = 0

    def read(self, gpio):
        return self.assigned_gpio_values[gpio]

pi = MockPi()

def test_motor_init():
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step == 1
    assert motor.direction == 2
    assert motor.ms1 == 3
    assert motor.ms2 == 4
    assert motor.ms3 == 5

def test_motor_move():
    motor = Motor(1, 2, 3, 4, 5, pi)
    motor.move(0.5, 20)  # Basic smoke test - should not raise exception

def test_motor_speed_too_slow():
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(1, 1)

def test_motor_speed_too_fast():
    motor = Motor(1, 2, 3, 4, 5, pi)
    with pytest.raises(Exception):
        motor.move(1, 1000)

def test_step_count_from_distance():
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step_count_from_distance(10) == 50
    assert motor.step_count_from_distance(0.5) == 2

def test_step_delay_from_speed():
    motor = Motor(1, 2, 3, 4, 5, pi)
    assert motor.step_delay_from_speed(20) == 10 / 1000.0

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
    
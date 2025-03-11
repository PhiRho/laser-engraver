import pytest
from laser_definition import Motor

def test_motor_init():
    """Test that Motor initializes with correct pin assignments"""
    motor = Motor(1, 2, 3, 4, 5)
    assert motor.step == 1
    assert motor.direction == 2
    assert motor.ms1 == 3
    assert motor.ms2 == 4
    assert motor.ms3 == 5

def test_motor_move():
    """Test motor move method"""
    motor = Motor(1, 2, 3, 4, 5)
    motor.move(100, 50)  # Basic smoke test - should not raise exception

def test_motor_arc_clockwise():
    """Test motor clockwise arc method"""
    motor = Motor(1, 2, 3, 4, 5)
    motor.arc_clockwise(10, 90, 50)  # Basic smoke test - should not raise exception

def test_motor_arc_counterclockwise():
    """Test motor counterclockwise arc method"""
    motor = Motor(1, 2, 3, 4, 5)
    motor.arc_counterclockwise(10, 90, 50)  # Basic smoke test - should not raise exception


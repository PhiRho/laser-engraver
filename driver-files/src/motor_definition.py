import logging
import pigpio
import time
from enum import Enum

class Motor:
    LOGGER = logging.getLogger(__name__)

    MICROSTEP_MATRIX = {
        1: (0, 0, 0),
        2: (1, 0, 0),
        4: (0, 1, 0),
        8: (1, 1, 0),
        16: (1, 1, 1)
    }

    Direction = Enum("Direction", [("CLOCKWISE", 0), ("COUNTERCLOCKWISE", 1)])

    STEPS_PER_REVOLUTION = 200
    TEETH_PER_REVOLUTION = 20
    TOOTH_PITCH = 2 # mm
    MM_PER_STEP = (TOOTH_PITCH * TEETH_PER_REVOLUTION) / STEPS_PER_REVOLUTION

    """
    A class to control a stepper motor. This assumes an A4988 stepper motor driver.

    Attributes:
        step: GPIO pin number for the step signal
        direction: GPIO pin number for the direction signal
        ms1: GPIO pin number for the ms1 signal
        ms2: GPIO pin number for the ms2 signal
        ms3: GPIO pin number for the ms3 signal
    """
    def __init__(self, step, direction, ms1, ms2, ms3, pi):
        self.step = step
        self.direction = direction
        self.ms1 = ms1
        self.ms2 = ms2
        self.ms3 = ms3
        self.pi = pi
        self.enable_pins()
        self.LOGGER.info("Motor initialized with pins: Step: %s, Direction: %s, MS1: %s, MS2: %s, MS3: %s", self.step, self.direction, self.ms1, self.ms2, self.ms3)
        self.set_microstep(1)

    def enable_pins(self):
        self.pi.set_mode(self.step, pigpio.OUTPUT)
        self.pi.set_mode(self.direction, pigpio.OUTPUT)
        self.pi.set_mode(self.ms1, pigpio.OUTPUT)
        self.pi.set_mode(self.ms2, pigpio.OUTPUT)
        self.pi.set_mode(self.ms3, pigpio.OUTPUT)

    def set_microstep(self, microstep):
        self.pi.write(self.ms1, self.MICROSTEP_MATRIX[microstep][0])
        self.pi.write(self.ms2, self.MICROSTEP_MATRIX[microstep][1])
        self.pi.write(self.ms3, self.MICROSTEP_MATRIX[microstep][2])
        self.LOGGER.info("Microstep set to: %s", microstep)

    def set_direction(self, direction):
        self.pi.write(self.direction, direction.value)
        self.LOGGER.info("Direction set to: %s", direction)

    def step_with_delay(self, delay):
        self.pi.write(self.step, 1)
        time.sleep(delay)
        self.pi.write(self.step, 0)

    def __str__(self):
        direction_state = self.pi.read(self.direction)
        direction = "COUNTERCLOCKWISE" if direction_state == 1 else "CLOCKWISE"
        return f"Motor(step={self.step}, direction={self.direction}[{direction}], ms1={self.ms1}, ms2={self.ms2}, ms3={self.ms3})"

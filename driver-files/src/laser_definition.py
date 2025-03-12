import logging
from motor_definition import Motor

class LaserDefinition:
    logger = logging.getLogger(__name__)
    """
    A class to control a laser cutter's motors and laser module. This assumes NEMA 17 stepper motors.

    Attributes:
        x_motor: Motor which moves the laser cutter in the x direction
        y_motor: Motor which moves the laser cutter in the y direction
        limit_pins: Limit switch pins (tuple of GPIO pins for end and movement limits)
        laser_pin: GPIO pin number for controlling the laser module
    """
    def __init__(self, x_motor, y_motor, limit_pins, laser_pin):
        self.x_motor = x_motor
        self.y_motor = y_motor
        self.limit_pins = limit_pins
        self.laser_pin = laser_pin

    def move_x(self, distance, speed):
        self.x_motor.move(distance, speed)

    # In order to move straight in the Y direction, the X motor has to turn too.
    def move_y(self, distance, speed):
        self.x_motor.move(distance, speed)
        self.y_motor.move(distance, speed)

    def arc_clockwise(self, radius, angle, speed):
        # TODO: Use the right distance-speed combos on x/y to get an arc
        pass

    def arc_counterclockwise(self, radius, angle, speed):
        # TODO: Use the right distance-speed combos on x/y to get an arc
        pass

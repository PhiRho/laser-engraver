import logging
import pigpio
import time

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

class Motor:
    LOGGER = logging.getLogger(__name__)

    MICROSTEP_MATRIX = {
        1: (0, 0, 0),
        2: (1, 0, 0),
        4: (0, 1, 0),
        8: (1, 1, 0),
        16: (1, 1, 1)
    }
    
    STEPS_PER_REVOLUTION = 200
    TEETH_PER_REVOLUTION = 20
    TOOTH_PITCH = 2 # mm
    
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

    """
    Attributes: 
        distance: Distance to move in mm
        speed: Speed to move at in mm/s
    """
    def move(self, distance, speed):
        full_revolution = self.TEETH_PER_REVOLUTION * self.TOOTH_PITCH
        # Distance is a number of steps
        step_count = self.step_count_from_distance(distance)
        # Speed is a number of steps per second, but we need to know the number of millis between steps
        step_delay = self.step_delay_from_speed(speed)

        # Moving too fast or too slow is going to cause problems with the smoothness of the movement, and 
        # will do interesting things to precision.
        if (step_delay > (100 / 1000.0)):
            raise Exception("Step delay is too long: ", step_delay)
        elif (step_delay < (1 / 1000.0)):
            raise Exception("Step delay is too short: ", step_delay)

        for i in range(step_count):
            self.pi.write(self.step, 1)
            time.sleep(step_delay)
            self.pi.write(self.step, 0)
            time.sleep(step_delay)  

    def step_count_from_distance(self, distance):
        full_revolution = self.TEETH_PER_REVOLUTION * self.TOOTH_PITCH
        return int(distance / full_revolution * self.STEPS_PER_REVOLUTION)

    def step_delay_from_speed(self, speed):
        full_revolution = self.TEETH_PER_REVOLUTION * self.TOOTH_PITCH
        steps_per_second = (speed / full_revolution) * self.STEPS_PER_REVOLUTION
        step_delay = (1.0 / steps_per_second) # Whilst the delay should be calculated in millis, the function works in seconds
        return step_delay


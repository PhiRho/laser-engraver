import logging
import pigpio
from motor_definition import Motor

class LaserDefinition:
    logger = logging.getLogger(__name__)
    """
    A class to control a laser cutter's motors and laser module. This assumes NEMA 17 stepper motors.

    Attributes:
        x_motor: Motor which moves the laser cutter in the x direction
        y_motor: Motor which moves the laser cutter in the y direction
        x_limits: Tuple of GPIO pins for movement limits
        y_limits: Tuple of GPIO pins for end limits
        laser_pin: GPIO pin number for controlling the laser module
    """
    def __init__(self, x_motor, y_motor, x_limits, y_limits, laser_pin, pi):
        self.x_motor = x_motor
        self.y_motor = y_motor
        self.x_limits = x_limits
        self.y_limits = y_limits
        self.laser_pin = laser_pin
        self.pi = pi
        self.setup_pins()
        self.location = (0, 0)
        self.stop_motor = False

    def setup_pins(self):
        self.pi.set_mode(self.x_limits[0], pigpio.INPUT)
        self.pi.set_pull_up_down(self.x_limits[0], pigpio.PUD_UP)
        self.pi.set_mode(self.x_limits[1], pigpio.INPUT)
        self.pi.set_pull_up_down(self.x_limits[1], pigpio.PUD_UP)
        self.pi.set_mode(self.y_limits[0], pigpio.INPUT)
        self.pi.set_pull_up_down(self.y_limits[0], pigpio.PUD_UP)
        self.pi.set_mode(self.y_limits[1], pigpio.INPUT)
        self.pi.set_pull_up_down(self.y_limits[1], pigpio.PUD_UP)
        self.pi.set_mode(self.laser_pin, pigpio.OUTPUT)

        self.pi.callback(self.x_limits[0], pigpio.EITHER_EDGE, self.interrupt_movement)
        self.pi.callback(self.x_limits[1], pigpio.EITHER_EDGE, self.interrupt_movement)
        self.pi.callback(self.y_limits[0], pigpio.EITHER_EDGE, self.interrupt_movement)
        self.pi.callback(self.y_limits[1], pigpio.EITHER_EDGE, self.interrupt_movement)

    """
    Moves both X and Y until the bump into specific limits, then sets that point as "home". 
    """
    def find_home(self):
        # TODO: Implement this
        pass

    def interrupt_movement(self, gpio, level, tick):
        # TODO: Send signal to break loops
        self.stop_motor = True
        if gpio == self.x_limits[0]:
            self.logger.info("X limit 0 hit")
            self.move_x(0.2, 1, Motor.Direction.CLOCKWISE)
        elif gpio == self.x_limits[1]:
            self.logger.info("X limit 1 hit")
            self.move_x(0.2, 1, Motor.Direction.COUNTERCLOCKWISE)
        elif gpio == self.y_limits[0]:
            self.logger.info("Y limit 0 hit")
            self.move_y(0.2, 1, Motor.Direction.CLOCKWISE)
        elif gpio == self.y_limits[1]:
            self.logger.info("Y limit 1 hit")
            self.move_y(0.2, 1, Motor.Direction.COUNTERCLOCKWISE)
        self.logger.info("GPIO %s has changed state with level %s", gpio, level)

    """Move in a straight line along the X Axis"""
    def move_x(self, distance, speed, direction):
        self.x_motor.set_direction(direction)
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        if direction.value == Motor.Direction.CLOCKWISE.value:
            step_size = Motor.MM_PER_STEP
        else:
            step_size = -Motor.MM_PER_STEP
        for i in range(step_count):
            self.x_motor.step_with_delay(step_delay)
            self.location = (self.location[0] + step_size, self.location[1])

    """
    Move in a stright line on the Y Axis
    As long as the delay is small enough, the line will be straight. 
    But since the motors are not being triggered in parallel this is an approximation at best.
    """
    def move_y(self, distance, speed, direction):
        self.x_motor.set_direction(direction)
        self.y_motor.set_direction(direction)
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        for i in range(step_count):
            self.x_motor.step_with_delay(step_delay)
            self.y_motor.step_with_delay(step_delay)
            self.location = (self.location[0], self.location[1] + Motor.MM_PER_STEP)

    def arc_clockwise(self, radius, angle, speed):
        # TODO: Use the right distance-speed combos on x/y to get an arc
        pass

    def arc_counterclockwise(self, radius, angle, speed):
        # TODO: Use the right distance-speed combos on x/y to get an arc
        pass

    def run_together(self, fun_1, fun_2):
        #TODO: Implement parallel processing such that two functions can run at the same time
        pass

    def step_count_from_distance(self, distance):
        full_revolution = Motor.TEETH_PER_REVOLUTION * Motor.TOOTH_PITCH
        return int(distance / full_revolution * Motor.STEPS_PER_REVOLUTION)

    def step_delay_from_speed(self, speed):
        # TODO: Add the microsteps required to hit high accuracy
        full_revolution = Motor.TEETH_PER_REVOLUTION * Motor.TOOTH_PITCH
        steps_per_second = (speed / full_revolution) * Motor.STEPS_PER_REVOLUTION
        step_delay = (1.0 / steps_per_second) # Whilst the delay should be calculated in millis, the function works in seconds
        return step_delay


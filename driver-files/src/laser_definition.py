import logging
import pigpio
import time
from motor_definition import Motor

class Laser:
    logger = logging.getLogger(__name__)
    """
    A class to control a laser cutter's motors and laser module. This assumes NEMA 17 stepper motors.

    Attributes:
        x_motor: Motor which moves the laser cutter in the x direction
        y_motor: Motor which moves the laser cutter in the y direction
        x_limits: Tuple of GPIO pins for movement limits
        y_limit: Pin number for end limit
        laser_pin: GPIO pin number for controlling the laser module
    """
    def __init__(self, x_motor, y_motor, x_limits, y_limit, laser_pin, pi):
        self.x_motor = x_motor
        self.y_motor = y_motor
        self.x_limits = x_limits
        self.y_limit = y_limit
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
        self.pi.set_mode(self.y_limit, pigpio.INPUT)
        self.pi.set_pull_up_down(self.y_limit, pigpio.PUD_UP)

        self.pi.callback(self.x_limits[0], pigpio.EITHER_EDGE, self.interrupt_movement)
        self.pi.callback(self.x_limits[1], pigpio.EITHER_EDGE, self.interrupt_movement)
        self.pi.callback(self.y_limit, pigpio.EITHER_EDGE, self.interrupt_movement)

    """
    Moves both X and Y until the bump into specific limits, then sets that point as "home". 
    """
    def find_home(self):
        self.move_x(300, 30, Motor.Direction.COUNTERCLOCKWISE)
        self.location[0] = 0
        self.move_y(600, 30, Motor.Direction.CLOCKWISE)
        self.location[1] = 0

    def interrupt_movement(self, gpio, level, tick):
        self.stop_motor = True
        time.sleep(0.01)
        if gpio == self.x_limits[0]:
            self.logger.info("X limit 0 hit")
            self.move_x(0.2, 1, Motor.Direction.COUNTERCLOCKWISE)
        elif gpio == self.x_limits[1]:
            self.logger.info("X limit 1 hit")
            self.move_x(0.2, 1, Motor.Direction.CLOCKWISE)
        elif gpio == self.y_limit:
            self.logger.info("Y limit hit")
            self.move_y(0.2, 1, Motor.Direction.CLOCKWISE)
        self.logger.info("GPIO %s has changed state with level %s", gpio, level)
        self.stop_motor = True

    """Move in a straight line along the X Axis"""
    def move_x(self, distance, speed, direction):
        self.x_motor.set_direction(direction)
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        if direction.value == Motor.Direction.COUNTERCLOCKWISE.value:
            step_size = Motor.MM_PER_STEP
        else:
            step_size = -Motor.MM_PER_STEP
        self.stop_motor = False
        for i in range(step_count):
            if self.stop_motor:
                self.logger.warn("Motor interrupted by limit")
                return
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
        self.y_motor.set_microstep(1)
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        if direction.value == Motor.Direction.CLOCKWISE.value:
            step_size = Motor.MM_PER_STEP
        else:
            step_size = -Motor.MM_PER_STEP
        self.stop_motor = False
        for i in range(step_count):
            if self.stop_motor:
                self.logger.warn("Motor interrupted by limit")
                return
            if self.location[1] + step_size > 650:
                self.logger.warn("Reached limit enforced by software on Y-Axis")
                return
            self.x_motor.step_with_delay(step_delay)
            self.y_motor.step_with_delay(step_delay)
            self.location = (self.location[0], self.location[1] + step_size)

    """Auto generated, needs serious checks"""
    def arc_clockwise(self, radius, angle, speed):
        """Move in a clockwise arc with given radius (mm), angle (degrees) and speed (mm/s)"""
        import math
        
        # Convert angle to radians for math functions
        angle_rad = math.radians(angle)
        
        # Calculate arc length and coordinates
        arc_length = radius * angle_rad
        num_segments = int(arc_length / (Motor.MM_PER_STEP * 2))  # Divide into small segments
        
        for i in range(num_segments):
            segment_angle = angle_rad * i / num_segments
            # Calculate x,y coordinates for this segment
            x = radius * (1 - math.cos(segment_angle))  # Distance from start in x
            y = radius * math.sin(segment_angle)        # Distance from start in y
            
            # Calculate deltas from previous position
            if i > 0:
                dx = x - prev_x
                dy = y - prev_y
                
                # Move x and y by the delta amounts
                if dx > 0:
                    self.move_x(abs(dx), speed, Motor.Direction.CLOCKWISE)
                else:
                    self.move_x(abs(dx), speed, Motor.Direction.COUNTERCLOCKWISE)
                    
                if dy > 0:
                    self.move_y(abs(dy), speed, Motor.Direction.CLOCKWISE) 
                else:
                    self.move_y(abs(dy), speed, Motor.Direction.COUNTERCLOCKWISE)
            
            prev_x = x
            prev_y = y

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


import logging
import math
import pigpio
import time
import numpy as np
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

        self.pi.callback(self.x_limits[0], pigpio.FALLING_EDGE, self.interrupt_movement)
        self.pi.callback(self.x_limits[1], pigpio.FALLING_EDGE, self.interrupt_movement)
        self.pi.callback(self.y_limit, pigpio.FALLING_EDGE, self.interrupt_movement)

    def set_home(self):
        self.location = (0, 0)

    """
    Called by `pigpio` when one of the limit switches is depressed. Required to ensure that the
    motors cannot overshoot their bounds.
    """
    def interrupt_movement(self, gpio, level, tick):
        self.stop_motor = True
        time.sleep(0.01)
        self.logger.info(f"GPIO {gpio} has changed state with level {level}")
        if gpio == self.x_limits[0]:
            self.logger.info("X limit 0 hit")
            self.move_x(10, 100, False)
        elif gpio == self.x_limits[1]:
            self.logger.info("X limit 1 hit")
            self.move_x(10, 100, True)
        elif gpio == self.y_limit:
            self.logger.info("Y limit hit")
            self.move_y(10, 100, True)
        self.logger.info(f"Motor move back 10mm")
        self.stop_motor = True

    """Move in a straight line along the X Axis"""
    def move_x(self, distance, speed, positive=True):
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        if positive:
            step_size = Motor.MM_PER_STEP
        else:
            step_size = -Motor.MM_PER_STEP
        self.stop_motor = False
        for i in range(step_count):
            if self.stop_motor:
                self.logger.warn("Motor interrupted by limit")
                break
            self.step_x(step_delay, positive)
            self.location = (self.location[0] + step_size, self.location[1])

    def step_x(self, delay, direction):
        if direction:
            self.x_motor.set_direction(Motor.Direction.CLOCKWISE)
        else:
            self.x_motor.set_direction(Motor.Direction.COUNTERCLOCKWISE)
        self.x_motor.step_with_delay(delay)

    """
    Move in a stright line on the Y Axis
    As long as the delay is small enough, the line will be straight.
    But since the motors are not being triggered in parallel this is an approximation at best.
    """
    def move_y(self, distance, speed, positive=True):
        self.y_motor.set_microstep(1)
        step_count = self.step_count_from_distance(distance)
        step_delay = self.step_delay_from_speed(speed)
        if positive:
            step_size = Motor.MM_PER_STEP
        else:
            step_size = -Motor.MM_PER_STEP
        self.stop_motor = False
        for i in range(step_count):
            if self.stop_motor:
                self.logger.warn("Motor interrupted by limit")
                break
            if self.location[1] + step_size > 650:
                self.logger.warn("Reached limit enforced by software on Y-Axis")
                break
            self.step_y(step_delay, positive)
            self.location = (self.location[0], self.location[1] + step_size)

    def step_y(self, delay, direction):
        if direction:
            self.x_motor.set_direction(Motor.Direction.CLOCKWISE)
            self.y_motor.set_direction(Motor.Direction.CLOCKWISE)
        else:
            self.x_motor.set_direction(Motor.Direction.COUNTERCLOCKWISE)
            self.y_motor.set_direction(Motor.Direction.COUNTERCLOCKWISE)

        self.x_motor.step_with_delay(delay)
        self.y_motor.step_with_delay(delay)

    """
    Move in a straight line at the specified angle (in degrees) for the given distance (mm) at speed (mm/s)
    Angle is measured from positive x-axis (0 degrees) counterclockwise
    """
    def move_angle(self, distance, speed, angle):
        # Normalize angle to 0-360
        angle = angle % 360

        # Handle cardinal directions
        cardinal_directions = {
            90: lambda: self.move_y(distance, speed, True),
            180: lambda: self.move_x(distance, speed, False),
            270: lambda: self.move_y(distance, speed, False),
            0: lambda: self.move_x(distance, speed, True),
            360: lambda: self.move_x(distance, speed, True)
        }

        if angle in cardinal_directions:
            return cardinal_directions[angle]()

        # Calculate quadrant-specific values
        quadrant_data = {
            (0, 90): (0, math.cos, math.sin, True, True),
            (90, 180): (90, math.sin, math.cos, False, True),
            (180, 270): (180, math.cos, math.sin, False, False),
            (270, 360): (270, math.sin, math.cos, True, False)
        }

        # Find the correct quadrant
        for (start, end), (subtract, x_func, y_func, x_dir, y_dir) in quadrant_data.items():
            if start < angle < end:
                angle_rad = math.radians(angle - subtract)
                x_dist = distance * x_func(angle_rad)
                y_dist = distance * y_func(angle_rad)
                x_direction, y_direction = x_dir, y_dir
                break

        # Calculate steps needed for each axis
        x_steps = self.step_count_from_distance(round(x_dist, 3))
        y_steps = self.step_count_from_distance(round(y_dist, 3))

        # Calculate step delay based on total distance and speed
        step_delay = self.step_delay_from_speed(speed)

        # Track position changes for location updates
        x_step_size = Motor.MM_PER_STEP if x_direction else -Motor.MM_PER_STEP
        y_step_size = Motor.MM_PER_STEP if y_direction else -Motor.MM_PER_STEP

        # Use the longer axis for the main loop
        total_steps = max(x_steps, y_steps)
        if total_steps == 0:
            return

        # Calculate step ratios
        x_ratio = x_steps / total_steps
        y_ratio = y_steps / total_steps

        x_accumulator = 0
        y_accumulator = 0

        self.stop_motor = False
        for i in range(total_steps):
            if self.stop_motor:
                self.logger.warn("Motor interrupted by limit")
                break

            # Check Y axis limit
            if y_step_size > 0 and self.location[1] + y_step_size > 600:
                self.logger.warn("Reached limit enforced by software on Y-Axis")
                break

            # Accumulate step fractions and step when they exceed 1
            x_accumulator += x_ratio
            y_accumulator += y_ratio

            if x_accumulator >= 1:
                self.step_x(step_delay, x_direction)
                self.location = (self.location[0] + x_step_size, self.location[1])
                x_accumulator -= 1

            if y_accumulator >= 1:
                self.step_y(step_delay, y_direction)
                self.location = (self.location[0], self.location[1] + y_step_size)
                y_accumulator -= 1

    def _safe_sqrt(self, x):
        """Safely calculate square root, handling negative values."""
        return np.sqrt(max(0, x))

    def _calculate_next_arc_point(self, current_point, center_x, center_y, radius, step_size, clockwise=True):
        """Calculate the next point on an arc.

        Args:
            current_point: [x, y] list of current position
            center_x, center_y: Center point of the arc
            radius: Radius of the arc
            step_size: Distance to move in x direction
            clockwise: True for clockwise movement, False for counterclockwise

        Returns:
            [x, y] list of next point
        """
        # Calculate the slope at current point to determine which axis to step
        dx = current_point[0] - center_x
        dy = current_point[1] - center_y
        slope = abs(dy / dx) if dx != 0 else 2.0

        # Determine direction multipliers based on clockwise parameter
        y_step = step_size if clockwise else -step_size
        x_step = step_size if clockwise else -step_size

        if dx >= 0 and dy > 0:  # First movement pattern (top right)
            if slope > 1:  # More vertical slope - step horizontally
                current_point[0] += x_step
                current_point[1] = center_y + self._safe_sqrt(radius**2 - (dx)**2)
            else:  # More horizontal slope - step vertically
                current_point[1] -= y_step
                current_point[0] = center_x + self._safe_sqrt(radius**2 - (dy)**2)
        elif dx > 0 and dy <= 0:  # Second movement pattern (bottom right)
            if slope > 1:  # More vertical slope - step horizontally
                current_point[0] -= x_step
                current_point[1] = center_y - self._safe_sqrt(radius**2 - (dx)**2)
            else:  # More horizontal slope - step vertically
                current_point[1] -= y_step
                current_point[0] = center_x + self._safe_sqrt(radius**2 - (dy)**2)
        elif dx <= 0 and dy < 0:  # Third movement pattern (bottom left)
            if slope > 1:  # More vertical slope - step horizontally
                current_point[0] -= x_step
                current_point[1] = center_y - self._safe_sqrt(radius**2 - (dx)**2)
            else:  # More horizontal slope - step vertically
                current_point[1] += y_step
                current_point[0] = center_x - self._safe_sqrt(radius**2 - (dy)**2)
        else:  # Fourth movement pattern (top left)
            if slope > 1:  # More vertical slope - step horizontally
                current_point[0] += x_step
                current_point[1] = center_y + self._safe_sqrt(radius**2 - (dx)**2)
            else:  # More horizontal slope - step vertically
                current_point[1] += y_step
                current_point[0] = center_x - self._safe_sqrt(radius**2 - (dy)**2)
        return current_point

    def _validate_arc_parameters(self, end_x, end_y, center_x, center_y):
        """Validate parameters for arc movement.

        Args:
            end_x, end_y: Target end position coordinates (mm)
            center_x, center_y: Coordinates of the arc's center point (mm)

        Returns:
            float: The radius of the arc

        Raises:
            ValueError: If end point has negative coordinates
            ValueError: If radius is zero
            ValueError: If end point is not same radius from center as start point
        """
        # Check end point coordinates
        if end_x < 0 or end_y < 0:
            raise ValueError("End point cannot have negative coordinates")

        # Calculate radius from center point to current position
        current_x, current_y = self.location
        radius = np.sqrt((current_x - center_x)**2 + (current_y - center_y)**2)

        if radius == 0:
            raise ValueError("Radius cannot be zero")

        # Verify end point is same radius from center
        end_radius = np.sqrt((end_x - center_x)**2 + (end_y - center_y)**2)
        if not np.isclose(radius, end_radius, rtol=1e-2, atol=1e-2):
            raise ValueError("End point must be same radius from center as start point")

        return radius

    def arc_clockwise(self, end_x, end_y, center_x, center_y, speed):
        """Move in a clockwise arc to a target position around a center point

        Args:
            end_x, end_y: Target end position coordinates (mm)
            center_x, center_y: Coordinates of the arc's center point (mm)
            speed: Movement speed in mm/s

        Raises:
            ValueError: If end point has negative coordinates
            ValueError: If radius is zero
            ValueError: If arc would pass through negative coordinates
        """
        # Validate parameters and get radius
        radius = self._validate_arc_parameters(end_x, end_y, center_x, center_y)

        # Use a small step size to ensure smooth movement
        step_size = Motor.MM_PER_STEP * 4 # if the step size is too small the motors get janky about it
        current_point = [self.location[0], self.location[1]]

        # Move along the arc until we reach the end point
        self.stop_motor = False
        while not self.stop_motor and (abs(current_point[0] - end_x) >= step_size or abs(current_point[1] - end_y) >= step_size):
            # Calculate next point based on current position
            current_point = self._calculate_next_arc_point(current_point, center_x, center_y, radius, step_size, clockwise=True)

            # Check if this movement would enter negative space
            if current_point[0] < 0 or current_point[1] < 0:
                self.stop_motor = True
                raise ValueError(f"Arc would pass through negative coordinates at {current_point[0]}, {current_point[1]}")

            # Move to the next point
            self.move_to(current_point[0], current_point[1], speed)
        # Move to the exact end point
        self.move_to(end_x, end_y, speed)

    def arc_counterclockwise(self, end_x, end_y, center_x, center_y, speed):
        """Move in a counterclockwise arc to a target position around a center point

        Args:
            end_x, end_y: Target end position coordinates (mm)
            center_x, center_y: Coordinates of the arc's center point (mm)
            speed: Movement speed in mm/s

        Raises:
            ValueError: If end point has negative coordinates
            ValueError: If radius is zero
            ValueError: If arc would pass through negative coordinates
        """
        # Validate parameters and get radius
        radius = self._validate_arc_parameters(end_x, end_y, center_x, center_y)

        # Use a small step size to ensure smooth movement
        step_size = Motor.MM_PER_STEP * 4 # if the step size is too small the motors get janky about it
        current_point = [self.location[0], self.location[1]]

        # Move along the arc until we reach the end point
        self.stop_motor = False
        while not self.stop_motor and (abs(current_point[0] - end_x) >= step_size or abs(current_point[1] - end_y) >= step_size):
            # Calculate next point based on current position
            current_point = self._calculate_next_arc_point(current_point, center_x, center_y, radius, step_size, clockwise=False)

            # Check if this movement would enter negative space
            if current_point[0] < 0 or current_point[1] < 0:
                self.stop_motor = True
                raise ValueError(f"Arc would pass through negative coordinates at {current_point[0]}, {current_point[1]}")

            # Move to the next point
            self.move_to(current_point[0], current_point[1], speed)
        # Move to the exact end point
        self.move_to(end_x, end_y, speed)

    def step_count_from_distance(self, distance):
        full_revolution = Motor.TEETH_PER_REVOLUTION * Motor.TOOTH_PITCH
        return int(distance / full_revolution * Motor.STEPS_PER_REVOLUTION)

    def step_delay_from_speed(self, speed):
        # TODO: Add the microsteps required to hit high accuracy
        full_revolution = Motor.TEETH_PER_REVOLUTION * Motor.TOOTH_PITCH
        steps_per_second = (speed / full_revolution) * Motor.STEPS_PER_REVOLUTION
        step_delay = (1.0 / steps_per_second) # Whilst the delay should be calculated in millis, the function works in seconds
        return step_delay

    def move_to(self, end_x, end_y, speed):
        """Move in a straight line to the specified coordinates

        Args:
            end_x, end_y: Target end position coordinates (mm)
            speed: Movement speed in mm/s

        Raises:
            ValueError: If target coordinates are negative
        """
        # Check for negative coordinates
        if end_x < 0 or end_y < 0:
            raise ValueError("Negative coordinates are not allowed")

        # Calculate distance and angle to target
        current_x, current_y = self.location
        dx = end_x - current_x
        dy = end_y - current_y

        # Calculate distance using Pythagorean theorem
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return

        # Calculate angle (atan2 returns angle in radians from -pi to pi)
        angle = math.degrees(math.atan2(dy, dx))
        self.logger.info(f"Angle to move: {angle}")

        # Normalize angle to 0-360 degrees
        if angle < 0:
            angle += 360

        # Use existing move_angle function to perform the movement
        self.move_angle(distance, speed, angle)


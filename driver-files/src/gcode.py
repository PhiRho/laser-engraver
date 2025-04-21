import os
import re
import logging
from laser_definition import Laser

logger = logging.getLogger(__name__)

class GCodeInterpreter:
    """
    A class to interpret GCode files and process instructions.
    """

    def __init__(self, laser=None):
        # Default settings
        self.mm_mode = True  # True for mm, False for inches
        self.absolute_mode = True  # True for absolute, False for relative
        self.laser_on = False
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_feed_rate = 1000.0  # Default feed rate
        self.previous_x = 0.0
        self.previous_y = 0.0
        self.laser = laser

    def read_file(self, file_path, dry_run=False):
        """
        Read a GCode file and process each line.

        Args:
            file_path (str): Path to the GCode file
            dry_run (bool): If True, parse the file without executing commands

        Returns:
            list: List of processed instructions
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.gc', '.gcode', '.g', '.txt']:
            raise ValueError(f"Unsupported file extension: {file_ext}")

        instructions = []

        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Process the line
                instruction = self._process_line(line, line_num, dry_run)
                if instruction:
                    instructions.append(instruction)

        if not dry_run and self.laser:
            logger.info(f"Executed {len(instructions)} instructions from {file_path}")
        elif dry_run:
            logger.info(f"Parsed {len(instructions)} instructions from {file_path} (dry run)")

        return instructions

    def _process_line(self, line, line_num, dry_run=False):
        """
        Process a single line of GCode.

        Args:
            line (str): The GCode line to process
            line_num (int): Line number for error reporting
            dry_run (bool): If True, parse the line without executing commands

        Returns:
            dict: Processed instruction or None if it's a comment
        """
        # Skip comments
        if line.startswith(';'):
            return None

        # Parse the line using regex to handle cases with no whitespace
        # This pattern matches commands like G1, G0, M3, etc. followed by parameters
        # with or without whitespace
        pattern = r'([GM]\d+)([XYZFEIJ][-+]?\d*\.?\d*)*'
        match = re.match(pattern, line)

        if not match:
            logger.warning(f"Could not parse line {line_num}: {line}")
            return None

        command = match.group(1)
        params = {}

        # Extract parameters using regex
        param_pattern = r'([XYZFEIJ])([-+]?\d*\.?\d*)'
        param_matches = re.findall(param_pattern, line)

        for param, value in param_matches:
            try:
                if value:  # Only convert if there's a value
                    params[param] = float(value)
            except ValueError:
                logger.warning(f"Invalid parameter value at line {line_num}: {param}{value}")

        # Process commands
        if command == 'G21':
            self.mm_mode = True
            return {'command': 'G21', 'description': 'Set units to millimeters'}

        elif command == 'G20':
            self.mm_mode = False
            return {'command': 'G20', 'description': 'Set units to inches'}

        elif command == 'G90':
            self.absolute_mode = True
            return {'command': 'G90', 'description': 'Set positioning to absolute'}

        elif command == 'G91':
            self.absolute_mode = False
            return {'command': 'G91', 'description': 'Set positioning to relative'}

        elif command == 'M05':
            self.laser_on = False
            if self.laser and not dry_run:
                self.laser.laser_off()
            return {'command': 'M05', 'description': 'Laser OFF'}

        elif command == 'M03':
            self.laser_on = True
            if self.laser and not dry_run:
                self.laser.laser_on()
            return {'command': 'M03', 'description': 'Laser ON'}

        elif command == 'G1':
            # Update feed rate if specified
            if 'F' in params:
                self.current_feed_rate = params['F']

            # Calculate new position
            new_x = self.current_x
            new_y = self.current_y

            if 'X' in params:
                if self.absolute_mode:
                    new_x = params['X']
                else:
                    new_x = self.current_x + params['X']

            if 'Y' in params:
                if self.absolute_mode:
                    new_y = params['Y']
                else:
                    new_y = self.current_y + params['Y']

            # Update position
            self.previous_x = self.current_x
            self.previous_y = self.current_y
            self.current_x = new_x
            self.current_y = new_y

            # Execute the movement if laser is available and not in dry run mode
            if self.laser and not dry_run:
                # Convert feed rate from mm/min to mm/s if in mm mode
                speed = self.current_feed_rate / 60.0 if self.mm_mode else self.current_feed_rate / 60.0 * 25.4
                self.laser.move_to(self.current_x, self.current_y, speed)

            return {
                'command': 'G1',
                'description': 'Linear move',
                'laser_on': self.laser_on,
                'x': self.current_x,
                'y': self.current_y,
                'feed_rate': self.current_feed_rate
            }

        elif command == 'G0':
            # Calculate new position
            new_x = self.current_x
            new_y = self.current_y

            if 'X' in params:
                if self.absolute_mode:
                    new_x = params['X']
                else:
                    new_x = self.current_x + params['X']

            if 'Y' in params:
                if self.absolute_mode:
                    new_y = params['Y']
                else:
                    new_y = self.current_y + params['Y']

            # Update position
            self.previous_x = self.current_x
            self.previous_y = self.current_y
            self.current_x = new_x
            self.current_y = new_y

            # Execute the movement if laser is available and not in dry run mode
            if self.laser and not dry_run:
                # For G0, use a fixed high speed (1000 mm/s)
                speed = 1000.0 if self.mm_mode else 1000.0 * 25.4
                self.laser.move_to(self.current_x, self.current_y, speed)

            return {
                'command': 'G0',
                'description': 'Rapid move',
                'laser_on': False,  # G0 always has laser off
                'x': self.current_x,
                'y': self.current_y
            }

        elif command == 'G2':
            # Update feed rate if specified
            if 'F' in params:
                self.current_feed_rate = params['F']

            # Calculate end position
            end_x = self.current_x
            end_y = self.current_y

            if 'X' in params:
                if self.absolute_mode:
                    end_x = params['X']
                else:
                    end_x = self.current_x + params['X']

            if 'Y' in params:
                if self.absolute_mode:
                    end_y = params['Y']
                else:
                    end_y = self.current_y + params['Y']

            # Calculate center point (I and J are relative to current position)
            center_x = self.current_x
            center_y = self.current_y

            if 'I' in params:
                center_x += params['I']

            if 'J' in params:
                center_y += params['J']

            # Update position
            self.previous_x = self.current_x
            self.previous_y = self.current_y
            self.current_x = end_x
            self.current_y = end_y

            # Execute the arc movement if laser is available and not in dry run mode
            if self.laser and not dry_run:
                # Convert feed rate from mm/min to mm/s if in mm mode
                speed = self.current_feed_rate / 60.0 if self.mm_mode else self.current_feed_rate / 60.0 * 25.4
                try:
                    self.laser.arc_clockwise(end_x, end_y, center_x, center_y, speed)
                except ValueError as e:
                    logger.error(f"Error executing G2 arc at line {line_num}: {e}")

            return {
                'command': 'G2',
                'description': 'Clockwise arc move',
                'laser_on': self.laser_on,
                'x': self.current_x,
                'y': self.current_y,
                'center_x': center_x,
                'center_y': center_y,
                'feed_rate': self.current_feed_rate
            }

        elif command == 'G3':
            # Update feed rate if specified
            if 'F' in params:
                self.current_feed_rate = params['F']

            # Calculate end position
            end_x = self.current_x
            end_y = self.current_y

            if 'X' in params:
                if self.absolute_mode:
                    end_x = params['X']
                else:
                    end_x = self.current_x + params['X']

            if 'Y' in params:
                if self.absolute_mode:
                    end_y = params['Y']
                else:
                    end_y = self.current_y + params['Y']

            # Calculate center point (I and J are relative to current position)
            center_x = self.current_x
            center_y = self.current_y

            if 'I' in params:
                center_x += params['I']

            if 'J' in params:
                center_y += params['J']

            # Update position
            self.previous_x = self.current_x
            self.previous_y = self.current_y
            self.current_x = end_x
            self.current_y = end_y

            # Execute the arc movement if laser is available and not in dry run mode
            if self.laser and not dry_run:
                # Convert feed rate from mm/min to mm/s if in mm mode
                speed = self.current_feed_rate / 60.0 if self.mm_mode else self.current_feed_rate / 60.0 * 25.4
                try:
                    self.laser.arc_counterclockwise(end_x, end_y, center_x, center_y, speed)
                except ValueError as e:
                    logger.error(f"Error executing G3 arc at line {line_num}: {e}")

            return {
                'command': 'G3',
                'description': 'Counterclockwise arc move',
                'laser_on': self.laser_on,
                'x': self.current_x,
                'y': self.current_y,
                'center_x': center_x,
                'center_y': center_y,
                'feed_rate': self.current_feed_rate
            }

        else:
            logger.warning(f"Unknown command at line {line_num}: {command}")
            return {'command': command, 'description': 'Unknown command', 'params': params}

    def get_current_state(self):
        """
        Get the current state of the interpreter.

        Returns:
            dict: Current state information
        """
        return {
            'mm_mode': self.mm_mode,
            'absolute_mode': self.absolute_mode,
            'laser_on': self.laser_on,
            'current_x': self.current_x,
            'current_y': self.current_y,
            'current_feed_rate': self.current_feed_rate
        }

    def execute_file(self, file_path):
        """
        Read and execute a GCode file using the connected laser.

        Args:
            file_path (str): Path to the GCode file

        Returns:
            list: List of executed instructions
        """
        if not self.laser:
            logger.error("No laser connected. Cannot execute GCode file.")
            return []

        return self.read_file(file_path, dry_run=False)

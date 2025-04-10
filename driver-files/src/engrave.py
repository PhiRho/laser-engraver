import logging
from laser_definition import Laser
from motor_definition import Motor
import configparser, os, cmd
from mock_pi import MockPi
import pigpio

logger = logging.getLogger(__name__)

class LaserShell(cmd.Cmd):

    intro = 'Welcome to the laser shell.   Type help or ? to list commands.\n'
    prompt = '(laser) '
    file = None

    def __init__(self):
        super().__init__()
        self.laser = None

    """Do not repeat the previous command (see https://docs.python.org/3/library/cmd.html#cmd.Cmd.emptyline)"""
    def emptyline(self):
        return

    def do_init(self, line):
        'Initialise the Laser device with the specified config file: init default_pins.ini'
        self.laser = initialise_laser(line)

    def do_print(self, line):
        'Print the current config: print'
        print(f"Location is currently {self.laser.location}")
        print(f"Motor X defined as {self.laser.x_motor}")
        print(f"Motor Y defined as {self.laser.y_motor}")
        print(f"X limits defined as {self.laser.x_limits}")
        print(f"Y limit defined as {self.laser.y_limit}")
        print(f"Laser pin defined as {self.laser.laser_pin}")

    def do_draw_to(self, line):
        'Draw a line from the current location to a given location (x,y) with a given speed (mm/s): draw_to 100 100 10'
        try:
            x, y, speed = parse_move_to(line)
            self.laser.laser_on()
            self.laser.move_to(x, y, speed)
            self.laser.laser_off()
        except (ValueError, TypeError) as e:
            print(f"Error executing draw_to command: {e}")
            print("Usage: draw_to <x> <y> <speed>")

    def do_move_x(self, line):
        'Move the laser a distance (in mm) on the X Axis at speed (in mm/s) and with direction (+/-): move_x 100 10 +'
        try:
            distance, speed, direction = parse_x_movement(line)
            self.laser.move_x(distance, speed, direction)
        except (ValueError, TypeError) as e:
            print(f"Error executing move_x command: {e}")
            print("Usage: move_x <distance> <speed> <direction>")
        except Exception as e:
            print(f"Error executing move_x command: {e}")

    def do_move_y(self, line):
        'Move the laser a distance (in mm) on the Y Axis at speed (in mm/s) and with direction (+/-): move_y 100 10 +'
        try:
            distance, speed, direction = parse_y_movement(line)
            self.laser.move_y(distance, speed, direction)
        except (ValueError, TypeError) as e:
            print(f"Error executing move_y command: {e}")
            print("Usage: move_y <distance> <speed> <direction>")
        except Exception as e:
            print(f"Error executing move_y command: {e}")

    def do_move_to(self, line):
        'Move the laser to a given location (x,y) with a given speed (mm/s): move_to 100 100 10'
        try:
            x, y, speed = parse_move_to(line)
            self.laser.move_to(x, y, speed)
        except (ValueError, TypeError) as e:
            print(f"Error executing move_to command: {e}")
            print("Usage: move_to <x> <y> <speed>")
        except Exception as e:
            print(f"Error executing move_to command: {e}")

    def do_cw_arc(self, line):
        'Move the laser in a clockwise arc ending at a location (x,y) with center point (i,j) and speed (mm/s): cw_arc 100 100 100 100 10'
        try:
            end_x, end_y, center_x, center_y, speed = parse_arc(line)
            self.laser.arc_clockwise(end_x, end_y, center_x, center_y, speed)
        except (ValueError, TypeError) as e:
            print(f"Error executing cw_arc command: {e}")
            print("Usage: cw_arc <end_x> <end_y> <center_x> <center_y> <speed>")
        except Exception as e:
            print(f"Error executing cw_arc command: {e}")

    def do_ccw_arc(self, line):
        'Move the laser in a counterclockwise arc ending at a location (x,y) with center point (i,j) and speed (mm/s): ccw_arc 100 100 100 100 10'
        try:
            end_x, end_y, center_x, center_y, speed = parse_arc(line)
            self.laser.arc_counterclockwise(end_x, end_y, center_x, center_y, speed)
        except (ValueError, TypeError) as e:
            print(f"Error executing ccw_arc command: {e}")
            print("Usage: ccw_arc <end_x> <end_y> <center_x> <center_y> <speed>")
        except Exception as e:
            print(f"Error executing ccw_arc command: {e}")

    def do_home(self, line):
        'Set the current location as home (0,0): home'
        self.laser.set_home()

    def do_angle(self, line):
        'Move the laser in a straight line for a given distance, with a given speed, at a given angle (degrees): angle 100 45 10'
        try:
            distance, speed, angle = parse_angle(line)
            self.laser.move_angle(distance, speed, angle)
        except (ValueError, TypeError) as e:
            print(f"Error executing angle command: {e}")
            print("Usage: angle <distance> <speed> <angle>")
        except Exception as e:
            print(f"Error executing angle command: {e}")

    def do_quit(self, line):
        'Quit the engraver: quit'
        if self.laser is not None:
            self.laser.pi.stop()
        return True

def parse_angle(line):
    distance, speed, angle = line.split()
    return int(distance), int(speed), int(angle)

def parse_move_to(line):
    x, y, speed = line.split()
    return float(x), float(y), float(speed)

def parse_x_movement(line):
    distance, speed, direction = line.split()
    if direction == "+":
        direction = True
    else:
        direction = False
    return int(distance), int(speed), direction

def parse_y_movement(line):
    distance, speed, direction = line.split()
    if direction == "-":
        direction = False
    else:
        direction = True
    return int(distance), int(speed), direction

def parse_arc(line):
    end_x, end_y, center_x, center_y, speed = line.split()
    return float(end_x), float(end_y), float(center_x), float(center_y), float(speed)

def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting engraver")
    LaserShell().cmdloop()
    logger.info("Engraver finished")

def initialise_laser(config_file):
    if not os.path.exists(config_file):
        logger.error(f"Config file {config_file} not found")
        return None
    config = configparser.ConfigParser()
    config.read(config_file)
    logger.info(f"Found sections {config.sections()}")

    if config.has_section('pi'):
        logger.info("Config has optional pi section")
        pi = MockPi()
    else:
        pi = pigpio.pi()
        if not pi.connected:
            logger.error("Failed to connect to pigpio; did you start the daemon?")
            return None

    x_motor_pins = config['xmotor']
    x_motor = Motor(int(x_motor_pins['step']), int(x_motor_pins['direction']), int(x_motor_pins['ms1']), int(x_motor_pins['ms2']), int(x_motor_pins['ms3']), pi)

    y_motor_pins = config['ymotor']
    y_motor = Motor(int(y_motor_pins['step']), int(y_motor_pins['direction']), int(y_motor_pins['ms1']), int(y_motor_pins['ms2']), int(y_motor_pins['ms3']), pi)

    limit_pins = config['limits']
    x_limits = (int(limit_pins['x_one']), int(limit_pins['x_two']))
    y_limit = int(limit_pins['y_one'])

    laser_pin = int(config['laser']['enable'])

    return Laser(x_motor, y_motor, x_limits, y_limit, laser_pin, pi)



if __name__ == "__main__":
    main()

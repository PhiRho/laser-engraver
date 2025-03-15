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

    def do_move_x(self, line):
        'Move the laser a distance (in mm) on the X Axis at speed (in mm/s) and with direction (+/-): move_x 100 10 +'
        distance, speed, direction = parse_movement(line)
        self.laser.move_x(distance, speed, direction)

    def do_move_y(self, line):
        'Move the laser a distance (in mm) on the Y Axis at speed (in mm/s) and with direction (+/-): move_y 100 10 +'
        distance, speed, direction = parse_movement(line)
        self.laser.move_y(distance, speed, direction)

    def do_cw_arc(self, line):
        'Move the laser in a clockwise arc with given radius (mm), angle (degrees) and speed (mm/s): cw_arc 100 45 10'
        radius, angle, speed = parse_arc(line)
        self.laser.arc_clockwise(radius, angle, speed)

    def do_home(self, line):
        'Move the laser to the home position: home'
        self.laser.find_home()

    def do_quit(self, line):
        'Quit the engraver: quit'
        if self.laser is not None:
            self.laser.pi.stop()
        return True

def parse_movement(line):
    distance, speed, direction = line.split()
    if direction == "+":
        direction = Motor.Direction.COUNTERCLOCKWISE
    else:
        direction = Motor.Direction.CLOCKWISE
    return int(distance), int(speed), direction

def parse_arc(line):
    radius, angle, speed = line.split()
    return int(radius), int(angle), int(speed)

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

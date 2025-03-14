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
        'Initialise the Laser device with the specified config file: INITIALISE default_pins.ini'
        self.laser = initialise_laser(line)

    def do_move_x(self, line):
        'Move the laser a distance (in mm) on the X Axis at speed (in mm/s) and with direction (+/-): MOVE_X 100 10 +'
        distance, speed, direction = parse_movement(line)
        self.laser.move_x(distance, speed, direction)

    def do_move_y(self, line):
        'Move the laser a distance (in mm) on the Y Axis at speed (in mm/s) and with direction (+/-): MOVE_Y 100 10 +'
        distance, speed, direction = parse_movement(line)
        self.laser.move_y(distance, speed, direction)

    def do_quit(self, line):
        'Quit the engraver: QUIT'
        if self.laser is not None:
            self.laser.pi.stop()
        return True

def parse_movement(line):
    'Parse the movement command: MOVE_X 100 10 +'
    distance, speed, direction = line.split()
    if direction == "+":
        direction = Motor.Direction.CLOCKWISE
    else:
        direction = Motor.Direction.COUNTERCLOCKWISE
    return int(distance), int(speed), direction

def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting engraver")
    LaserShell().cmdloop()
    logger.info("Engraver finished")

def initialise_laser(config_file):
    if not os.path.exists(config_file):
        logger.error("Config file %s not found", config_file)
        return None
    config = configparser.ConfigParser()
    config.read(config_file)
    logger.info("Found sections %s", config.sections())

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
    y_motor = Motor(y_motor_pins['step'], y_motor_pins['direction'], y_motor_pins['ms1'], y_motor_pins['ms2'], y_motor_pins['ms3'], pi)

    limit_pins = config['limits']
    x_limits = (int(limit_pins['x_one']), int(limit_pins['x_two']))
    y_limits = (int(limit_pins['y_one']), None)

    laser_pin = config['laser']['enable']

    return Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)



if __name__ == "__main__":
    main()

import logging
from laser_definition import Laser
from motor_definition import Motor
import configparser

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG)
    logger.info("Starting engraver")
    # TODO: Do something
    logger.info("Engraver finished")

def initialise_laser(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    x_motor_pins = config['x_motor']
    x_motor = Motor(x_motor_pins['step'], x_motor_pins['direction'], x_motor_pins['ms1'], x_motor_pins['ms2'], x_motor_pins['ms3'])

    y_motor_pins = config['y_motor']
    y_motor = Motor(y_motor_pins['step'], y_motor_pins['direction'], y_motor_pins['ms1'], y_motor_pins['ms2'], y_motor_pins['ms3'])

    limit_pins = config['limits']
    x_limits = (int(limit_pins['x_one']), int(limit_pins['x_two']))
    y_limits = (int(limit_pins['y_one']), int(limit_pins['y_two']))

    laser_pin = config['laser']['enable']

    return Laser(x_motor, y_motor, x_limits, y_limits, laser_pin)



if __name__ == "__main__":
    main()

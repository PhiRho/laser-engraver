import logging
import pigpio

logging.basicConfig(level=logging.DEBUG)

class MockPi(pigpio.pi):
    log = logging.getLogger(__name__)
    assigned_gpio_values = {}

    def __init__(self):
        super().__init__()

    def write(self, gpio, value):
        self.log.debug("write %s %s", gpio, value)
        self.assigned_gpio_values[gpio] = value

    def set_mode(self, gpio, mode):
        self.log.debug("set_mode %s %s", gpio, mode)
        self.assigned_gpio_values[gpio] = 0

    def read(self, gpio):
        return self.assigned_gpio_values[gpio]

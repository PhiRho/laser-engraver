from src.engrave import initialise_laser

def test_initialise_laser():
    laser = initialise_laser("test_pins.ini")
    assert laser is not None

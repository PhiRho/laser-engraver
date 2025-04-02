import pytest
from src.laser_definition import Laser
from src.mock_pi import MockPi
from src.motor_definition import Motor

# Important to note, all of these pin numbers are dummies. DO NOT USE THEM ON A REAL PI.
pi = MockPi()
x_motor = Motor(1, 2, 3, 4, 5, pi)
y_motor = Motor(6, 7, 8, 9, 10, pi)
x_limits = (11, 12)
y_limits = (13, 14)
laser_pin = 15

def test_laser_definition_init():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.pi == pi

def test_step_count_from_distance():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.step_count_from_distance(10) == 50
    assert laser.step_count_from_distance(0.5) == 2

def test_step_delay_from_speed():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    assert laser.step_delay_from_speed(20) == 10 / 1000.0

def test_move_x():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    laser.move_x(1, 1, Motor.Direction.CLOCKWISE)
    assert laser.location[0] == -1
    laser.move_x(1, 1, Motor.Direction.COUNTERCLOCKWISE)
    assert laser.location[0] <= 0.0001

def test_interrupt_movement():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    x_pos = laser.location[0]
    laser.interrupt_movement(x_limits[1], 1, 0)
    assert laser.stop_motor == True
    assert round(laser.location[0]) == x_pos - 10

def test_move_y():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    laser.move_y(1, 1, Motor.Direction.CLOCKWISE)
    assert laser.location[1] == -1
    laser.move_y(1, 1, Motor.Direction.COUNTERCLOCKWISE)
    assert laser.location[1] <= 0.0001

def test_move_angle():
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)
    laser.move_angle(5, 1, 37)
    assert pytest.approx(laser.location[0], 0.01) == 3.8
    assert pytest.approx(laser.location[1], 0.01) == 3

    laser.set_home()
    laser.move_angle(50, 100, 150)
    assert pytest.approx(laser.location[0], 0.01) == -43.3
    assert pytest.approx(laser.location[1], 0.01) == 25

    laser.set_home()
    laser.move_angle(80, 100, 210)
    assert pytest.approx(laser.location[0], 0.01) == -40
    assert pytest.approx(laser.location[1], 0.01) == -69.28

    laser.set_home()
    laser.move_angle(40, 100, 300)
    assert pytest.approx(laser.location[0], 0.01) == 34.64
    assert pytest.approx(laser.location[1], 0.01) == -20

def test_move_to():
    """Test move_to method with various cases"""
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)

    # Test diagonal movement
    laser.set_home()
    laser.move_to(100, 100, 50)
    assert pytest.approx(laser.location[0], 0.01) == 100
    assert pytest.approx(laser.location[1], 0.01) == 100

    # Test zero movement (should not change position)
    current_x, current_y = laser.location
    laser.move_to(current_x, current_y, 50)
    assert pytest.approx(laser.location[0], 0.01) == current_x
    assert pytest.approx(laser.location[1], 0.01) == current_y

    # Test cardinal directions
    laser.set_home()
    # Pure X movement
    laser.move_to(100, 0, 50)
    assert pytest.approx(laser.location[0], 0.01) == 100
    assert pytest.approx(laser.location[1], 0.01) == 0

    laser.set_home()
    # Pure Y movement
    laser.move_to(0, 100, 50)
    assert pytest.approx(laser.location[0], 0.01) == 0
    assert pytest.approx(laser.location[1], 0.01) == 100

    # Test negative coordinates should raise ValueError
    laser.set_home()
    with pytest.raises(ValueError, match="Negative coordinates are not allowed"):
        laser.move_to(-50, -50, 50)

    with pytest.raises(ValueError, match="Negative coordinates are not allowed"):
        laser.move_to(-30, 40, 50)

    with pytest.raises(ValueError, match="Negative coordinates are not allowed"):
        laser.move_to(30, -40, 50)

def test_arc_clockwise():
    """Test arc_clockwise method with various cases"""
    laser = Laser(x_motor, y_motor, x_limits, y_limits, laser_pin, pi)

    # Test small angle movement in quad 4
    laser.set_home()
    laser.arc_clockwise(50, 50, 50, 0, 150)
    assert pytest.approx(laser.location[0], abs=0.5) == 50
    assert pytest.approx(laser.location[1], abs=0.5) == 50

    # Test small angle movement in quad 3
    laser.set_home()
    laser.move_to(50, 0, 150)
    laser.arc_clockwise(0, 50, 50, 50, 150)
    assert pytest.approx(laser.location[0], abs=0.5) == 0
    assert pytest.approx(laser.location[1], abs=0.5) == 50

    # Test small angle movement in quad 2
    laser.set_home()
    laser.move_to(50, 50, 150)
    laser.arc_clockwise(0, 0, 0, 50, 150)
    assert pytest.approx(laser.location[0], abs=0.5) == 0
    assert pytest.approx(laser.location[1], abs=0.5) == 0

    # Test 90-degree clockwise arc in first quadrant
    laser.set_home()
    laser.move_to(0, 100, 150)  # Move to start position
    laser.arc_clockwise(100, 0, 0, 0, 150)  # 90° clockwise from (0,100) to (100,0)
    assert pytest.approx(laser.location[0], abs=0.5) == 100.0
    assert pytest.approx(laser.location[1], abs=0.5) == 0.0

    # Test zero radius case (error)
    laser.set_home()
    with pytest.raises(ValueError, match="Radius cannot be zero"):
        laser.arc_clockwise(1, 1, 0, 0, 50)  # Start point same as center point

    # Test mismatched radius case (error)
    laser.move_to(100, 0, 150)  # Move to radius 100
    with pytest.raises(ValueError, match="End point must be same radius from center as start point"):
        laser.arc_clockwise(50, 50, 0, 0, 50)  # End point at different radius than start point

    # Test non-integer movements
    laser.set_home()
    laser.move_to(0, 50.6, 150)  # Move to non-integer start position
    laser.arc_clockwise(50.6, 0, 0, 0, 150)  # 90° clockwise with non-integer radius
    assert pytest.approx(laser.location[0], abs=0.5) == 50.6
    assert pytest.approx(laser.location[1], abs=0.5) == 0

    # Test small angle movement
    laser.set_home()
    laser.move_to(0, 50, 150)
    laser.arc_clockwise(25, 43.3, 0, 0, 150)  # ~30° clockwise arc
    assert pytest.approx(laser.location[0], abs=0.5) == 25
    assert pytest.approx(laser.location[1], abs=0.5) == 43.3

    # Test movement with offset center (45° clockwise)
    laser.set_home()
    laser.move_to(150, 150, 150)
    laser.arc_clockwise(175, 125, 150, 125, 150)  # Arc around point (150,125) with 25 radius
    assert pytest.approx(laser.location[0], 0.01) == 175
    assert pytest.approx(laser.location[1], 0.01) == 125

    # Test negative end coordinates (error)
    with pytest.raises(ValueError, match="End point cannot have negative coordinates"):
        laser.arc_clockwise(-10, -10, 0, 0, 50)

    # Test larger angle (180° clockwise)
    laser.set_home()
    laser.move_to(0, 50, 150)  # Start at (0,100)
    laser.arc_clockwise(0, 0, 0, 25, 150)  # Half circle from top to bottom, center at (0,50)
    assert pytest.approx(laser.location[0], 0.01) == 0
    assert pytest.approx(laser.location[1], 0.01) == 0


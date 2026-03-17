import numpy as np
import pytest
from mvp.simulator import MotionSimulator

def test_simulator_init():
    sim = MotionSimulator(work_area_size=(500, 500), camera_fov=(50, 50), pixels_per_mm=2)
    assert sim.gantry_x == 0
    assert sim.gantry_y == 0
    assert sim.camera_fov_px == (100, 100)
    assert sim.work_area.shape == (500, 500, 3)

def test_simulator_move():
    sim = MotionSimulator()
    sim.move_gantry_to(10, 20)
    assert sim.gantry_x == 10
    assert sim.gantry_y == 20
    assert sim.camera_x_mm == 10
    assert sim.camera_y_mm == 20

def test_simulator_set_work_area():
    sim = MotionSimulator()
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    sim.set_work_area_image(img)
    assert sim.work_area.shape == (200, 200, 3)

def test_simulator_get_camera_view():
    sim = MotionSimulator(work_area_size=(100, 100), camera_fov=(20, 20), pixels_per_mm=1)
    # Fill work area with a pattern
    sim.work_area[:] = 0
    sim.work_area[40:60, 40:60] = 255 # White square in the middle
    
    sim.move_gantry_to(50, 50)
    view = sim.get_camera_view()
    
    # View should be 20x20
    assert view.shape == (20, 20, 3)
    # Center of view should be white
    assert np.all(view == 255)

def test_simulator_move_laser_to_marker():
    # pixels_per_mm = 5
    # laser_offset = (10, 10)
    sim = MotionSimulator(pixels_per_mm=5)
    sim.move_gantry_to(0, 0)
    
    # Marker is at center of camera view (50, 50) in pixels
    # FOV is 100x100 px (20x20 mm)
    marker_center_px = (500 / 2, 500 / 2) # Center of 500x500 px FOV
    
    sim.move_laser_to_marker_center(marker_center_px)
    
    # Marker absolute position should be (0, 0) mm
    # To place laser at (0, 0), gantry must be at (0 - 10, 0 - 10) = (-10, -10)
    assert sim.gantry_x == -10
    assert sim.gantry_y == -10

import numpy as np
import cv2
import pytest
from mvp.camera_simulator import CameraSimulator

def test_camera_simulator_init():
    sim = CameraSimulator(camera_fov=(100, 100), pixels_per_mm=5)
    assert sim.simulator is not None
    assert sim.recognizer is not None

def test_camera_simulator_move():
    sim = CameraSimulator()
    sim.move_to(50, 50)
    assert sim.simulator.gantry_x == 50
    assert sim.simulator.gantry_y == 50

def test_camera_simulator_get_frame():
    sim = CameraSimulator()
    frame = sim.get_frame()
    # Initial state is 1000x1000 white work area, 100x100mm FOV, 5px/mm
    # FOV is 500x500 pixels. But gantry is at (0, 0), so it's cropped to (250, 250)
    assert frame.shape == (250, 250, 3)

def test_camera_simulator_find_marker():
    pixels_per_mm = 5
    sim = CameraSimulator(camera_fov=(100, 100), pixels_per_mm=pixels_per_mm)
    sim.move_to(50, 50)
    
    # Manually draw a marker that we KNOW should be recognized 
    # based on test_recognizer.py success
    # Camera center at (50, 50)mm is (250, 250)px
    # Let's draw a hollow square 20x20px at (250, 250)px
    
    # Work area is 1000x1000px white
    wa = sim.simulator.work_area
    wa[:] = 255
    
    # Outer square (hollow)
    cv2.rectangle(wa, (240, 240), (260, 260), (0, 0, 0), 2)
    # Inner feature (detached)
    cv2.rectangle(wa, (248, 248), (252, 252), (0, 0, 0), -1)
    
    found, center = sim.find_marker()
    assert found
    # In FOV (250, 250) is the center
    assert abs(center[0] - 250) <= 2
    assert abs(center[1] - 250) <= 2

def test_camera_simulator_move_laser_to_marker():
    sim = CameraSimulator()
    sim.move_to(0, 0)
    
    # Marker at center of current FOV (500x500 pixels)
    marker_center_px = (250, 250)
    
    sim.move_laser_to_marker(marker_center_px)
    
    # marker abs pos (0, 0), laser_offset (10, 10)
    # gantry must move to (-10, -10)
    assert sim.simulator.gantry_x == -10
    assert sim.simulator.gantry_y == -10

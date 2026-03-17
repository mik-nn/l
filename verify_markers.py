import cv2
import numpy as np
from mvp.camera_simulator import CameraSimulator
import os

def test_marker_integration():
    # 1. Initialize camera simulator
    # Create a blank 200x200mm work area at 10 pixels/mm = 2000x2000 pixels
    sim = CameraSimulator(camera_fov=(50, 50), pixels_per_mm=10)
    sim.simulator.work_area = np.ones((2000, 2000, 3), dtype=np.uint8) * 255
    
    # 2. Add M1: Square at (50, 50) pointing towards (150, 150)
    # Angle in radians: atan2(150-50, 150-50) = atan2(100, 100) = 45 deg
    sim.add_marker(50, 50, "square", 45)
    
    # 3. Add M2: Circle at (150, 150) pointing towards (50, 50)
    # Angle: atan2(50-150, 50-150) = atan2(-100, -100) = -135 deg or 225 deg
    sim.add_marker(150, 150, "circle", 225)
    
    # 4. Move camera to M1 and save frame
    sim.move_to(50, 50)
    frame1 = sim.get_frame()
    if frame1 is not None:
        cv2.imwrite("test_m1_square.png", frame1)
        print("M1 square frame saved to test_m1_square.png")
    
    # 5. Move camera to M2 and save frame
    sim.move_to(150, 150)
    frame2 = sim.get_frame()
    if frame2 is not None:
        cv2.imwrite("test_m2_circle.png", frame2)
        print("M2 circle frame saved to test_m2_circle.png")

if __name__ == "__main__":
    test_marker_integration()

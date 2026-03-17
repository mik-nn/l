# mvp/camera_simulator.py
import cv2
import os
import sys

# Add the project root to the Python path to support direct execution
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mvp.simulator import MotionSimulator
from mvp.recognizer import MarkerRecognizer

class CameraSimulator:
    """
    A simulator that mimics a camera looking at a workspace image.
    It uses MotionSimulator to handle gantry movement and view cropping.
    """
    def __init__(self, workspace_image_path=None, camera_fov=(100, 100), pixels_per_mm=5):
        self.simulator = MotionSimulator(camera_fov=camera_fov, pixels_per_mm=pixels_per_mm)
        self.recognizer = MarkerRecognizer()
        
        if workspace_image_path:
            self.load_workspace(workspace_image_path)
            
    def load_workspace(self, image_path):
        """Loads the workspace image into the simulator."""
        image = cv2.imread(image_path)
        if image is not None:
            self.simulator.set_work_area_image(image)
        else:
            print(f"Warning: Could not load workspace image from {image_path}")

    def add_marker(self, x_mm, y_mm, shape_type, target_angle_deg, rotate_deg=0):
        """Adds a marker to the simulated workspace."""
        self.simulator.add_marker(x_mm, y_mm, shape_type, target_angle_deg, rotate_deg=rotate_deg)

    def move_to(self, x_mm, y_mm):
        """Moves the simulated camera to the specified coordinates."""
        self.simulator.move_gantry_to(x_mm, y_mm)

    def get_frame(self):
        """Returns the current camera view (frame)."""
        return self.simulator.get_camera_view()

    def find_marker(self):
        """Returns if a marker is found, its center, and its shape type."""
        frame = self.get_frame()
        if frame is None or frame.size == 0:
            return False, None, None
        return self.recognizer.find_marker(frame)

    def move_laser_to_marker(self, marker_center_px):
        """Moves the gantry so the laser is at the marker center."""
        self.simulator.move_laser_to_marker_center(marker_center_px)

    def release(self):
        """No-op for simulator."""
        pass

if __name__ == "__main__":
    # Simple standalone verification
    sim = CameraSimulator("HoneyComb.jpg")
    sim.move_to(50, 50)
    frame = sim.get_frame()
    if frame is not None:
        cv2.imwrite("test_camera_sim_frame.png", frame)
        print("Frame saved to test_camera_sim_frame.png")
    else:
        print("Failed to get frame from simulator.")

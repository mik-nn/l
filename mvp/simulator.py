# simulator.py
import numpy as np

class MotionSimulator:
    def __init__(self, work_area_size=(1000, 1000), camera_fov=(100, 100), pixels_per_mm=5):
        self.work_area = np.ones(work_area_size, dtype=np.uint8) * 255
        self.gantry_x = 0  # in mm
        self.gantry_y = 0  # in mm
        self.laser_offset_x = 10  # in mm
        self.laser_offset_y = 10  # in mm
        self.camera_fov_mm = camera_fov  # in mm
        self.pixels_per_mm = pixels_per_mm
        self.camera_fov_px = (
            int(self.camera_fov_mm[0] * self.pixels_per_mm),
            int(self.camera_fov_mm[1] * self.pixels_per_mm),
        )

        # The camera is mounted on the gantry, its position is the gantry position
        self.camera_x_mm = self.gantry_x
        self.camera_y_mm = self.gantry_y

    def get_camera_view(self):
        """
        Returns the view from the camera.
        The view is a crop of the work area.
        """
        camera_x_px = int(self.camera_x_mm * self.pixels_per_mm)
        camera_y_px = int(self.camera_y_mm * self.pixels_per_mm)

        half_fov_px_x = self.camera_fov_px[0] // 2
        half_fov_px_y = self.camera_fov_px[1] // 2

        start_x = camera_x_px - half_fov_px_x
        end_x = camera_x_px + half_fov_px_x
        start_y = camera_y_px - half_fov_px_y
        end_y = camera_y_px + half_fov_px_y

        # Make sure the view is within the work area
        start_x = max(0, start_x)
        end_x = min(self.work_area.shape[1], end_x)
        start_y = max(0, start_y)
        end_y = min(self.work_area.shape[0], end_y)
        
        return self.work_area[start_y:end_y, start_x:end_x]

    def move_gantry_to(self, x_mm, y_mm):
        """Moves the gantry to the specified position in mm."""
        self.gantry_x = x_mm
        self.gantry_y = y_mm
        self.camera_x_mm = self.gantry_x
        self.camera_y_mm = self.gantry_y
        print(f"Gantry moved to: ({self.gantry_x}, {self.gantry_y})")

    def move_laser_to_marker_center(self, marker_center_camera_px):
        """
        Moves the gantry so the laser is at the marker's center.
        marker_center_camera_px is the marker's center in the camera's view in pixels.
        """
        # 1. Convert marker center from camera view pixels to mm relative to camera center
        marker_offset_x_px = marker_center_camera_px[0] - self.camera_fov_px[0] / 2
        marker_offset_y_px = marker_center_camera_px[1] - self.camera_fov_px[1] / 2
        
        marker_offset_x_mm = marker_offset_x_px / self.pixels_per_mm
        marker_offset_y_mm = marker_offset_y_px / self.pixels_per_mm

        # 2. Calculate the marker's absolute position in mm
        marker_abs_x_mm = self.camera_x_mm + marker_offset_x_mm
        marker_abs_y_mm = self.camera_y_mm + marker_offset_y_mm
        
        # 3. Calculate the target gantry position to align laser with marker
        target_gantry_x = marker_abs_x_mm - self.laser_offset_x
        target_gantry_y = marker_abs_y_mm - self.laser_offset_y
        
        self.move_gantry_to(target_gantry_x, target_gantry_y)
        print(f"Laser is now at marker center: ({marker_abs_x_mm}, {marker_abs_y_mm})")


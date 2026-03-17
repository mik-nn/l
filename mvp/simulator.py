# simulator.py
import numpy as np

class MotionSimulator:
    def __init__(self, work_area_size=(1000, 1000), camera_fov=(100, 100), pixels_per_mm=5):
        # Work area is BGR by default
        self.work_area = np.ones((work_area_size[1], work_area_size[0], 3), dtype=np.uint8) * 255
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

    def set_work_area_image(self, image):
        """Sets the background image for the work area."""
        self.work_area = image
        # Optionally update size if image is different
        print(f"Work area image set. Size: {self.work_area.shape[1]}x{self.work_area.shape[0]}")

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

    def add_marker(self, x_mm, y_mm, shape_type, target_angle_deg, rotate_deg=0):
        """
        Adds a marker of the specified type at the given position.
        The marker's arrow will point in the specified direction.
        rotate_deg: overall rotation of the sample (relative to machine X axis).
        """
        from generate_marker import generate_marker
        import tempfile
        import os
        import cv2

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Generate marker with the arrow pointing to the target, 
            # taking into account the sample rotation.
            generate_marker(shape_type, target_angle_deg - rotate_deg, tmp_path, scale=self.pixels_per_mm)
            marker_img = cv2.imread(tmp_path)
            if marker_img is not None:
                # Rotate the entire marker image if the sample is rotated
                if rotate_deg != 0:
                    h, w = marker_img.shape[:2]
                    M = cv2.getRotationMatrix2D((w//2, h//2), rotate_deg, 1.0)
                    marker_img = cv2.warpAffine(marker_img, M, (w, h), borderValue=(255, 255, 255))

                h, w = marker_img.shape[:2]
                center_x_px = int(x_mm * self.pixels_per_mm)
                center_y_px = int(y_mm * self.pixels_per_mm)
                
                start_x = center_x_px - w // 2
                start_y = center_y_px - h // 2
                
                # Ensure we are within bounds
                y1, y2 = max(0, start_y), min(self.work_area.shape[0], start_y + h)
                x1, x2 = max(0, start_x), min(self.work_area.shape[1], start_x + w)
                
                if y2 <= y1 or x2 <= x1: return

                marker_roi = marker_img[y1-start_y:y2-start_y, x1-start_x:x2-start_x]
                work_roi = self.work_area[y1:y2, x1:x2]
                
                # Overlay marker onto work area using a mask for transparency
                # Any pixel that is not pure white is considered part of the marker
                gray_marker = cv2.cvtColor(marker_roi, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray_marker, 250, 255, cv2.THRESH_BINARY_INV)
                
                # Use the mask to overlay
                if work_roi.shape[:2] == marker_roi.shape[:2]:
                    img_bg = cv2.bitwise_and(work_roi, work_roi, mask=cv2.bitwise_not(mask))
                    img_fg = cv2.bitwise_and(marker_roi, marker_roi, mask=mask)
                    self.work_area[y1:y2, x1:x2] = cv2.add(img_bg, img_fg)
            else:
                print(f"Error: Could not load generated marker from {tmp_path}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def place_sample(self, image_path, center_x_mm, center_y_mm, rotate_deg=0, scale=1.0):
        """
        Places a sample image on the work area with rotation, scaling and transparency.
        """
        import cv2
        import numpy as np
        sample = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if sample is None:
            print(f"Error: Could not load sample image from {image_path}")
            return

        # Handle scaling
        if scale != 1.0:
            h, w = sample.shape[:2]
            new_size = (int(w * scale), int(h * scale))
            sample = cv2.resize(sample, new_size, interpolation=cv2.INTER_LINEAR)

        # Handle rotation
        h, w = sample.shape[:2]
        if rotate_deg != 0:
            M = cv2.getRotationMatrix2D((w//2, h//2), rotate_deg, 1.0)
            # Calculate bounding box for rotation to avoid clipping
            cos = np.abs(M[0, 0])
            sin = np.abs(M[0, 1])
            nW = int((h * sin) + (w * cos))
            nH = int((h * cos) + (w * sin))
            M[0, 2] += (nW / 2) - w // 2
            M[1, 2] += (nH / 2) - h // 2
            sample = cv2.warpAffine(sample, M, (nW, nH), borderValue=(255, 255, 255))

        h, w = sample.shape[:2]
        start_x = int(center_x_mm * self.pixels_per_mm) - w // 2
        start_y = int(center_y_mm * self.pixels_per_mm) - h // 2

        # Ensure we are within bounds
        y1, y2 = max(0, start_y), min(self.work_area.shape[0], start_y + h)
        x1, x2 = max(0, start_x), min(self.work_area.shape[1], start_x + w)
        
        if y2 <= y1 or x2 <= x1: 
            print(f"Sample at ({center_x_mm}, {center_y_mm}) is out of bounds")
            return

        sample_roi = sample[y1-start_y:y2-start_y, x1-start_x:x2-start_x]
        work_roi = self.work_area[y1:y2, x1:x2]

        # Just overlay the sample (including its white background)
        if sample_roi.shape[2] == 4:
            # Use alpha channel if present
            alpha = sample_roi[:, :, 3:4] / 255.0
            work_roi[:] = (sample_roi[:, :, :3] * alpha + work_roi * (1.0 - alpha)).astype(np.uint8)
        else:
            # Direct copy
            self.work_area[y1:y2, x1:x2] = sample_roi[:, :, :3]

        print(f"Sample placed at ({center_x_mm}, {center_y_mm}) with scale {scale} and rotation {rotate_deg}")

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


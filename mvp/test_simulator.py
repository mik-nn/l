# mvp/test_simulator.py
import cv2
import numpy as np
from simulator import MotionSimulator
from recognizer import MarkerRecognizer

def main():
    # 1. Initialize simulator and recognizer
    simulator = MotionSimulator()
    recognizer = MarkerRecognizer()

    # 2. Load marker and place it on the work area
    marker_img = cv2.imread("markers/marker.png", cv2.IMREAD_GRAYSCALE)
    if marker_img is None:
        print("Error: Could not load marker image.")
        return
        
    marker_h, marker_w = marker_img.shape
    marker_pos_px = (300, 400)
    simulator.work_area[marker_pos_px[1]:marker_pos_px[1]+marker_h, marker_pos_px[0]:marker_pos_px[0]+marker_w] = marker_img

    # 3. Move gantry to see the marker
    # The marker is at (300,400) px, which is (60, 80) mm
    gantry_target_mm = (60, 80)
    simulator.move_gantry_to(gantry_target_mm[0], gantry_target_mm[1])
    
    # 4. Get camera view and find the marker
    camera_view_gray = simulator.get_camera_view()
    # Recognizer needs a 3-channel image
    camera_view_bgr = cv2.cvtColor(camera_view_gray, cv2.COLOR_GRAY2BGR)

    found, center_px = recognizer.find_marker(camera_view_bgr)

    if found:
        print(f"Marker found in camera view at: {center_px} px")
        
        # 5. Move laser to marker center
        simulator.move_laser_to_marker_center(center_px)
        
        # 6. Verification
        # laser position in mm is gantry position + laser offset
        laser_pos_mm_x = simulator.gantry_x + simulator.laser_offset_x
        laser_pos_mm_y = simulator.gantry_y + simulator.laser_offset_y
        
        # marker position in mm
        marker_center_pos_mm_x = (marker_pos_px[0] + marker_w / 2) / simulator.pixels_per_mm
        marker_center_pos_mm_y = (marker_pos_px[1] + marker_h / 2) / simulator.pixels_per_mm

        print(f"Final laser position (mm): ({laser_pos_mm_x:.2f}, {laser_pos_mm_y:.2f})")
        print(f"Marker center position (mm): ({marker_center_pos_mm_x:.2f}, {marker_center_pos_mm_y:.2f})")

        # Check if the laser is at the marker center
        # There might be some small error due to pixel discretization
        if abs(laser_pos_mm_x - marker_center_pos_mm_x) < 1 and abs(laser_pos_mm_y - marker_center_pos_mm_y) < 1:
            print("Test Passed: Laser is at the marker center.")
        else:
            print("Test Failed: Laser is not at the marker center.")

    else:
        print("Marker not found in camera view.")
        # For debugging, save the camera view
        cv2.imwrite("debug_camera_view.png", camera_view_gray)

if __name__ == "__main__":
    main()

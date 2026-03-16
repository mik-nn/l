# mvp/app.py
from .simulator import MotionSimulator
from .recognizer import MarkerRecognizer
from .bridge import get_bridge
import cv2

class Application:
    def __init__(self):
        self.simulator = MotionSimulator()
        self.recognizer = MarkerRecognizer()
        self.bridge = get_bridge()
        self.state = "first_marker_search"
        
        # Place marker on work area for simulation
        marker_img = cv2.imread("markers/marker.png", cv2.IMREAD_GRAYSCALE)
        if marker_img is not None:
            marker_h, marker_w = marker_img.shape
            # Place two markers
            self.marker1_pos_px = (200, 200)
            self.marker2_pos_px = (600, 200)
            self.simulator.work_area[self.marker1_pos_px[1]:self.marker1_pos_px[1]+marker_h, self.marker1_pos_px[0]:self.marker1_pos_px[0]+marker_w] = marker_img
            self.simulator.work_area[self.marker2_pos_px[1]:self.marker2_pos_px[1]+marker_h, self.marker2_pos_px[0]:self.marker2_pos_px[0]+marker_w] = marker_img
            print("Placed two markers on the simulated work area.")
        else:
            print("Could not load marker image for simulation.")

    def run(self):
        print("Starting LaserCam MVP application.")
        print("Move the gantry to find the first marker.")
        
        # Initial gantry position to see the first marker
        self.simulator.move_gantry_to(
            self.marker1_pos_px[0] / self.simulator.pixels_per_mm,
            self.marker1_pos_px[1] / self.simulator.pixels_per_mm
        )

        while True:
            camera_view = self.simulator.get_camera_view()
            camera_view_bgr = cv2.cvtColor(camera_view, cv2.COLOR_GRAY2BGR)
            
            found, center = self.recognizer.find_marker(camera_view_bgr)

            if self.state == "first_marker_search" and found:
                print("First marker found. Press '1' to confirm.")
                self.state = "first_marker_confirm"
            
            if self.state == "first_marker_confirm":
                if self.bridge.check_for_hotkey():
                    self.simulator.move_laser_to_marker_center(center)
                    print("First marker confirmed. Move to the second marker.")
                    self.state = "second_marker_search"
                    # Move gantry to see the second marker
                    self.simulator.move_gantry_to(
                        self.marker2_pos_px[0] / self.simulator.pixels_per_mm,
                        self.marker2_pos_px[1] / self.simulator.pixels_per_mm
                    )

            if self.state == "second_marker_search" and found:
                print("Second marker found. Press '1' to confirm.")
                self.state = "second_marker_confirm"

            if self.state == "second_marker_confirm":
                if self.bridge.check_for_hotkey():
                    self.simulator.move_laser_to_marker_center(center)
                    print("Second marker confirmed. Alignment complete.")
                    break
            
            cv2.imshow("Simulator Camera View", camera_view_bgr)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()

def main():
    app = Application()
    app.run()

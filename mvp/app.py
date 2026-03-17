# mvp/app.py
import cv2
import os
import sys

# Add the project root to the Python path to support direct execution
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mvp.camera_simulator import CameraSimulator
from mvp.ui import App
from mvp.bridge import get_bridge

class Application:
    def __init__(self, use_simulator=True):
        if use_simulator:
            self.camera = CameraSimulator("HoneyComb.jpg")
            
            import random
            import math
            rotate_deg = random.uniform(0, 360)
            
            # Marker 1 and 2 base positions relative to machine center (to land on mesh)
            m1_base = (150, 200)
            m2_base = (300, 350)
            
            # Rotate positions around a central anchor on the mesh
            mid_x, mid_y = 220, 270
            
            def rotate_pos(pos, mid, angle_deg):
                rad = math.radians(angle_deg)
                dx, dy = pos[0] - mid[0], pos[1] - mid[1]
                rx = mid[0] + dx * math.cos(rad) - dy * math.sin(rad)
                ry = mid[1] + dx * math.sin(rad) + dy * math.cos(rad)
                return rx, ry
            
            m1_x, m1_y = rotate_pos(m1_base, (mid_x, mid_y), rotate_deg)
            m2_x, m2_y = rotate_pos(m2_base, (mid_x, mid_y), rotate_deg)
            
            # Target angles relative to machine X
            angle12 = math.degrees(math.atan2(m2_y - m1_y, m2_x - m1_x))
            angle21 = angle12 + 180
            
            # Place markers on the simulator
            self.camera.add_marker(m1_x, m1_y, 'square', angle12, rotate_deg=rotate_deg)
            self.camera.add_marker(m2_x, m2_y, 'circle', angle21, rotate_deg=rotate_deg)
            
            # If TestPrint.png exists, place it too (centered between markers)
            sample_mid_x, sample_mid_y = (m1_x + m2_x) / 2, (m1_y + m2_y) / 2
            if os.path.exists("TestPrint.png"):
                self.camera.simulator.place_sample("TestPrint.png", sample_mid_x, sample_mid_y, rotate_deg=rotate_deg)
                print(f"Placed TestPrint.png at ({sample_mid_x}, {sample_mid_y}) with {rotate_deg:.2f} deg")
            
            print(f"Placed markers with sample rotation: {rotate_deg:.2f} deg")
        else:
            from mvp.camera import Camera
            self.camera = Camera()

        self.bridge = get_bridge()
        self.ui = App(camera=self.camera)
        
        # Initial gantry position
        if use_simulator:
            self.camera.move_to(m1_x, m1_y) # Start exactly at the first marker

    def run(self):
        self.ui.mainloop()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()

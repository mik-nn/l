# ui.py
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import sys

# Add the project root to the Python path to support direct execution
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from mvp.camera import Camera

class App(tk.Tk):
    def __init__(self, camera=None, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("LaserCam MVP")
        self.camera = camera if camera else Camera()
        
        # Main layout
        self.main_frame = tk.Frame(self)
        self.main_frame.pack()

        # FOV view
        self.canvas = tk.Canvas(self.main_frame, width=640, height=480)
        self.canvas.pack(side=tk.LEFT)
        
        # Overview view
        self.overview_canvas = tk.Canvas(self.main_frame, width=400, height=400)
        self.overview_canvas.pack(side=tk.RIGHT)
        
        # Control panel
        self.control_panel = tk.Frame(self)
        self.control_panel.pack()
        
        from mvp.camera_simulator import CameraSimulator
        if isinstance(self.camera, CameraSimulator):
            self.add_simulator_controls()

        self.delay = 15
        self.update()

    def add_simulator_controls(self):
        btn_frame = tk.Frame(self.control_panel)
        btn_frame.pack()
        
        step = 5 # mm
        
        tk.Button(btn_frame, text="Up", command=lambda: self.move_sim(0, -step)).grid(row=0, column=1)
        tk.Button(btn_frame, text="Left", command=lambda: self.move_sim(-step, 0)).grid(row=1, column=0)
        tk.Button(btn_frame, text="Right", command=lambda: self.move_sim(step, 0)).grid(row=1, column=2)
        tk.Button(btn_frame, text="Down", command=lambda: self.move_sim(0, step)).grid(row=2, column=1)
        
    def move_sim(self, dx, dy):
        from mvp.camera_simulator import CameraSimulator
        if isinstance(self.camera, CameraSimulator):
            sim = self.camera.simulator
            sim.move_gantry_to(sim.gantry_x + dx, sim.gantry_y + dy)

    def update(self):
        # 1. Update FOV view
        frame = self.camera.get_frame()
        if frame is not None:
            # Detect markers for visualization
            from mvp.camera_simulator import CameraSimulator
            if isinstance(self.camera, CameraSimulator):
                found, center = self.camera.find_marker()
                if found:
                    cv2.circle(frame, center, 10, (0, 255, 0), 2)
                    cv2.putText(frame, "Marker Found", (center[0]+15, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Resize frame to fit canvas if needed
            h, w = frame.shape[:2]
            if w > 640 or h > 480:
                frame = cv2.resize(frame, (640, 480))
                
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
        # 2. Update Overview view if it's a simulator
        from mvp.camera_simulator import CameraSimulator
        if isinstance(self.camera, CameraSimulator):
            sim = self.camera.simulator
            work_area = sim.work_area
            
            # Resize work area for overview
            overview_img = cv2.resize(work_area, (400, 400))
            overview_rgb = cv2.cvtColor(overview_img, cv2.COLOR_BGR2RGB)
            self.overview_photo = ImageTk.PhotoImage(image=Image.fromarray(overview_rgb))
            self.overview_canvas.create_image(0, 0, image=self.overview_photo, anchor=tk.NW)
            
            # Draw camera FOV rectangle
            # Map gantry coordinates to overview pixels
            # work_area size
            wa_h, wa_w = work_area.shape[:2]
            scale_x = 400 / wa_w
            scale_y = 400 / wa_h
            
            cam_x_px = sim.camera_x_mm * sim.pixels_per_mm
            cam_y_px = sim.camera_y_mm * sim.pixels_per_mm
            
            fov_w_px = sim.camera_fov_px[0]
            fov_h_px = sim.camera_fov_px[1]
            
            rect_x1 = (cam_x_px - fov_w_px/2) * scale_x
            rect_y1 = (cam_y_px - fov_h_px/2) * scale_y
            rect_x2 = (cam_x_px + fov_w_px/2) * scale_x
            rect_y2 = (cam_y_px + fov_h_px/2) * scale_y
            
            self.overview_canvas.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2, outline="red", width=2)

        self.after(self.delay, self.update)

    def on_closing(self):
        self.camera.release()
        self.destroy()

def main():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()

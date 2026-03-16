# ui.py
import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from .camera import Camera

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("LaserCam MVP")
        self.camera = Camera()
        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()
        self.delay = 15
        self.update()

    def update(self):
        frame = self.camera.get_frame()
        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
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

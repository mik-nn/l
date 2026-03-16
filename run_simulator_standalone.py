import cv2
from lasercam.meerk40t_camera_simulator.meerk40t_camera_simulator.simulator import MockCapture

def main():
    """
    Runs the camera simulator as a standalone application,
    displaying its output in a window.
    """
    print("Starting standalone camera simulator...")
    print("Press 'q' in the window to quit.")

    # 1. Create an instance of the MockCapture
    simulator_capture = MockCapture(width=800, height=600)
    simulator_capture.fps = 30 # Set a higher FPS for smoother animation

    # 2. Loop to read and display frames
    while True:
        ret, frame = simulator_capture.read()
        if not ret:
            print("Simulator stopped.")
            break

        # 3. Display the frame
        cv2.imshow("Meerk40t Camera Simulator - Standalone", frame)
        print(f"Displaying frame {simulator_capture.frame_count}...")

        # 4. Check for exit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 5. Clean up
    simulator_capture.release()
    cv2.destroyAllWindows()
    print("Simulator closed.")

if __name__ == "__main__":
    main()

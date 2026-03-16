# recognizer.py
import cv2
import numpy as np

class MarkerRecognizer:
    def find_marker(self, frame):
        """
        Finds a square marker in the frame.
        This is a simple implementation that looks for a square contour.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)

        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)

            if len(approx) == 4:
                # This is a quadrilateral. Now check if it's a square.
                (x, y, w, h) = cv2.boundingRect(approx)
                ar = w / float(h)

                # A square will have an aspect ratio of approximately 1
                if ar >= 0.95 and ar <= 1.05:
                    # Found the marker
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        return True, (cX, cY)

        return False, None

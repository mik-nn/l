# recognizer.py
import cv2
import numpy as np

class MarkerRecognizer:
    def find_marker(self, frame):
        """
        Finds a marker in the frame. Supports square and circle shapes.
        """
        if frame is None or frame.size == 0:
            return False, None
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Use Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Adaptive thresholding is better for picking up small local features in complex backgrounds
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)

        # Use RETR_TREE to get hierarchy information
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if hierarchy is None:
            return False, None

        for i, contour in enumerate(contours):
            # Check if this contour has a child (potential arrow inside)
            # hierarchy[0][i][2] is the index of the first child
            if hierarchy[0][i][2] == -1:
                continue

            area = cv2.contourArea(contour)
            if area < 50 or area > 50000: # Slightly broader range
                continue
                
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
            
            is_candidate = False
            shape_type = None
            # Check if it's a square
            if len(approx) == 4:
                # Use minAreaRect for rotated squares
                rect = cv2.minAreaRect(contour)
                (x, y), (w, h), angle = rect
                if h > 0:
                    ar = w / float(h)
                    if 0.7 <= ar <= 1.4: # Lenient for rotated squares on noisy background
                        is_candidate = True
                        shape_type = 'square'
            
            # Check if it's a circle using circularity
            if not is_candidate and peri > 0:
                circularity = 4 * np.pi * area / (peri * peri)
                if circularity > 0.8: # Lenient
                    is_candidate = True
                    shape_type = 'circle'

            if is_candidate:
                child_idx = hierarchy[0][i][2]
                valid_internal = False
                
                cX_p, cY_p = self._get_center(contour)[1]
                marker_size = np.sqrt(area)

                while child_idx != -1:
                    child_area = cv2.contourArea(contours[child_idx])
                    ratio = child_area / area
                    
                    # Internal feature (arrow) should be small (up to 20% of parent area)
                    if 0.005 < ratio < 0.2:
                        if self._is_valid_internal(contours[child_idx], cX_p, cY_p, marker_size):
                            valid_internal = True
                            break
                    elif ratio >= 0.2:
                        # This might be a hole in a hollow marker. Check grandchildren.
                        grandchild_idx = hierarchy[0][child_idx][2]
                        while grandchild_idx != -1:
                            grandchild_area = cv2.contourArea(contours[grandchild_idx])
                            g_ratio = grandchild_area / area
                            if 0.005 < g_ratio < 0.2:
                                if self._is_valid_internal(contours[grandchild_idx], cX_p, cY_p, marker_size):
                                    valid_internal = True
                                    break
                            grandchild_idx = hierarchy[0][grandchild_idx][0]
                        if valid_internal:
                            break
                    child_idx = hierarchy[0][child_idx][0]
                
                if valid_internal:
                    return True, (cX_p, cY_p), shape_type

        return False, None, None

    def _is_valid_internal(self, contour, cX_p, cY_p, marker_size):
        M_c = cv2.moments(contour)
        if M_c["m00"] != 0:
            cX_c = int(M_c["m10"] / M_c["m00"])
            cY_c = int(M_c["m01"] / M_c["m00"])
            
            # Distance between centers
            dist = np.sqrt((cX_c - cX_p)**2 + (cY_c - cY_p)**2)
            # Internal feature should be roughly centered
            if dist < marker_size * 0.6:
                return True
        return False

    def _get_center(self, contour):
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return True, (cX, cY)
        return False, None

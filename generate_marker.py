import cv2
import numpy as np

# Create a white image
marker_size = 200
image = np.ones((marker_size, marker_size), dtype=np.uint8) * 255

# Create a black square in the center
square_size = 100
start_point = (marker_size - square_size) // 2
end_point = start_point + square_size
cv2.rectangle(image, (start_point, start_point), (end_point, end_point), (0, 0, 0), -1)

# Save the image
cv2.imwrite("marker.png", image)

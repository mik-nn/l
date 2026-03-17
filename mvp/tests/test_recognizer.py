import numpy as np
import cv2
import pytest
from mvp.recognizer import MarkerRecognizer

@pytest.fixture
def recognizer():
    return MarkerRecognizer()

def test_find_marker_positive(recognizer):
    # Create a white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Draw a hollow black square marker (stroke 2)
    cv2.rectangle(img, (40, 40), (60, 60), (0, 0, 0), 2)
    # Add an internal feature (the arrow)
    cv2.rectangle(img, (48, 48), (52, 52), (0, 0, 0), -1)
    
    found, center = recognizer.find_marker(img)
    assert found
    assert abs(center[0] - 50) <= 1
    assert abs(center[1] - 50) <= 1

def test_find_marker_negative(recognizer):
    # Create a white image with no marker
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    found, center = recognizer.find_marker(img)
    assert not found
    assert center is None

def test_find_marker_no_internal(recognizer):
    # Create a white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Draw a hollow square but NO internal arrow
    cv2.rectangle(img, (40, 40), (60, 60), (0, 0, 0), 2)
    
    found, center = recognizer.find_marker(img)
    # Should NOT be found because it lacks internal validation
    assert not found

def test_find_marker_circle(recognizer):
    # Create a white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Draw a hollow black circle marker
    cv2.circle(img, (50, 50), 10, (0, 0, 0), 2)
    # Add internal feature
    cv2.circle(img, (50, 50), 3, (0, 0, 0), -1)
    
    found, center = recognizer.find_marker(img)
    assert found
    assert abs(center[0] - 50) <= 1
    assert abs(center[1] - 50) <= 1

def test_find_marker_hollow_with_arrow(recognizer):
    # Create a white image
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    # Draw a hollow square (stroke)
    cv2.rectangle(img, (40, 40), (60, 60), (0, 0, 0), 2)
    # Draw a small circle inside to simulate internal feature (arrow part)
    cv2.circle(img, (50, 50), 3, (0, 0, 0), -1)
    
    found, center = recognizer.find_marker(img)
    assert found
    assert abs(center[0] - 50) <= 1
    assert abs(center[1] - 50) <= 1

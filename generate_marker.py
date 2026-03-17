import cv2
import numpy as np
import argparse
import math

def draw_arrow(image, center, angle_rad, color=(0, 0, 0), scale=10):
    """
    Draws an arrow pointing in the given direction.
    Modified to ensure the arrow stem does NOT touch the marker boundary,
    making it a detached internal feature for better recognition.
    """
    # Constants from JSX (in mm, converted to pixels via scale)
    # Total stem length will be 1.0mm (from 0.5mm to 1.5mm)
    stem_start = 0.5 * scale
    stem_end = 1.5 * scale
    arrow_thick = int(0.6 * scale)
    arrow_head = 1.2 * scale
    tip_offset = 1.5 * scale # Offset from marker center to head tip
    
    cx, cy = center
    
    # Arrow stem (detached internal feature)
    x1 = cx + stem_start * math.cos(angle_rad)
    y1 = cy + stem_start * math.sin(angle_rad)
    x2 = cx + stem_end * math.cos(angle_rad)
    y2 = cy + stem_end * math.sin(angle_rad)
    
    cv2.line(image, (int(x1), int(y1)), (int(x2), int(y2)), color, max(1, arrow_thick))
    
    # Detached triangle head (outside the shape)
    # Shape radius is 2.0mm, so we place the head further out
    head_dist = 2.5 * scale
    hx = cx + head_dist * math.cos(angle_rad)
    hy = cy + head_dist * math.sin(angle_rad)
    
    left_angle = angle_rad + math.pi * 0.75
    right_angle = angle_rad - math.pi * 0.75
    
    lx = hx + arrow_head * math.cos(left_angle)
    ly = hy + arrow_head * math.sin(left_angle)
    
    rx = hx + arrow_head * math.cos(right_angle)
    ry = hy + arrow_head * math.sin(right_angle)
    
    pts = np.array([[hx, hy], [lx, ly], [rx, ry]], np.int32)
    cv2.fillPoly(image, [pts], color)

def create_base_image(marker_size_mm, scale):
    size_px = int(marker_size_mm * scale)
    image = np.ones((size_px, size_px, 3), dtype=np.uint8) * 255
    return image, size_px // 2

def generate_marker(shape_type, target_angle_deg, output_path, scale=20):
    """
    Generates a marker image.
    shape_type: 'square' or 'circle'
    target_angle_deg: angle towards the other marker
    """
    marker_size_mm = 12.0 # Total canvas size in mm
    shape_size_mm = 4.0
    stroke_width_mm = 0.5 # Increased for better contrast
    
    image, center_px = create_base_image(marker_size_mm, scale)
    center = (center_px, center_px)
    
    color = (0, 0, 0)
    stroke_px = max(1, int(stroke_width_mm * scale))
    shape_px = int(shape_size_mm * scale)
    
    if shape_type == 'square':
        half = shape_px // 2
        top_left = (center_px - half, center_px - half)
        bottom_right = (center_px + half, center_px + half)
        cv2.rectangle(image, top_left, bottom_right, color, stroke_px)
    elif shape_type == 'circle':
        cv2.circle(image, center, shape_px // 2, color, stroke_px)
    
    # Add a small central dot as a reliable internal feature for recognition
    dot_radius = max(1, int(0.5 * scale)) # Increased for better contrast
    cv2.circle(image, center, dot_radius, color, -1)
    
    # Draw arrow pointing to target
    angle_rad = math.radians(target_angle_deg)
    draw_arrow(image, center, angle_rad, color, scale)
    
    cv2.imwrite(output_path, image)
    print(f"Generated {shape_type} marker at {output_path} with angle {target_angle_deg} deg")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate advanced markers for LaserCam")
    parser.add_argument("--type", choices=["square", "circle"], required=True, help="Marker shape type")
    parser.add_argument("--angle", type=float, default=0, help="Angle in degrees for the arrow")
    parser.add_argument("--output", type=str, default="marker.png", help="Output file path")
    parser.add_argument("--scale", type=int, default=20, help="Pixels per mm (DPI equivalent)")
    
    args = parser.parse_args()
    generate_marker(args.type, args.angle, args.output, args.scale)

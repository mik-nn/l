# Modules

This document describes all major modules of the Marker Alignment Tool.  
It covers both the **MVP implementation (Python)** and the **final implementation (C/C++/Qt)**, while keeping the external behaviour identical across both stages.

---

## 1. Camera Module

### Purpose
Provide real‑time video frames from the GigE camera using DirectShow, abstracted behind a stable API.

### Responsibilities
- Open the camera as a DirectShow video device.
- Deliver frames at a stable FPS.
- Expose resolution, FOV, and camera parameters.
- Provide timestamps for synchronization.
- In MVP: Python `cv2.VideoCapture(..., cv2.CAP_DSHOW)`.
- In final tool: DirectShow or Media Foundation capture in C/C++.

### Inputs
- Device index or DirectShow device name.
- Optional configuration (resolution, exposure, gain).

### Outputs
- Raw frames (RGB or grayscale).
- Camera metadata (resolution, FPS).

---

## 2. Marker Recognizer

### Purpose
Detect custom printed markers in the camera frame and compute their geometric properties.

### Responsibilities
- Locate marker candidates in the image.
- Validate marker shape and pattern.
- Compute marker center in image coordinates.
- Optionally compute orientation and confidence.
- Provide a stable API for “marker found / not found”.

### Inputs
- Current camera frame.

### Outputs
- `found: bool`
- `center: (x, y)` in image coordinates
- `orientation` (optional)
- `confidence` score

### Notes
- MVP uses Python + OpenCV for rapid iteration.
- Final tool re‑implements the stable algorithm in C/C++.

---

## 3. Motion Simulator

### Purpose
Simulate gantry movement, camera position, and laser offset during MVP development.

### Responsibilities
- Represent virtual X/Y coordinates of the gantry.
- Represent camera offset relative to the laser.
- Simulate movement commands (“move camera to marker”, “move laser to marker center”).
- Render camera FOV over a virtual work area.
- Visualize where the laser would cut relative to printed artwork.

### Inputs
- Target coordinates.
- Virtual work area image.
- Camera FOV parameters.

### Outputs
- Updated simulated positions.
- Visualization overlays.

### Notes
- Exists only in MVP; final tool uses real hardware movement.

---

## 4. LightBurn Bridge

### Purpose
Integrate with LightBurn’s Print & Cut workflow by detecting user actions and maintaining alignment state.

### Responsibilities
- Detect LightBurn main window (PID + EnumWindows).
- Track when LightBurn is the active window.
- Intercept Alt+F1 (and other Print & Cut hotkeys).
- Maintain Print & Cut state machine:
  - `idle`
  - `first_marker`
  - `second_marker`
  - `ready`
- Notify the rest of the system when the user selects a marker in LightBurn.

### Inputs
- OS window events.
- Keyboard events (Alt+F1).

### Outputs
- State transitions.
- Signals to move camera/laser to next marker.

### Notes
- MVP uses Python WinAPI bindings.
- Final tool uses native WinAPI hooks in C/C++.

---

## 5. UI Layer

### Purpose
Provide visual feedback, overlays, and user confirmations.

### Responsibilities
- Display live camera feed.
- Overlay detected markers and bounding boxes.
- Show “marker found / confirm” dialog.
- Display simulated work area and laser alignment.
- Provide controls for starting/stopping the Print & Cut assist flow.

### Inputs
- Frames from camera module.
- Marker recognizer output.
- Simulator or hardware positions.

### Outputs
- User confirmations.
- Visual overlays.

### Notes
- MVP UI: wxPython or minimal custom window.
- Final UI: Qt (C++).

---

## 6. Coordinate Mapping Module

### Purpose
Convert between camera image coordinates, gantry coordinates, and laser coordinates.

### Responsibilities
- Maintain camera‑to‑laser offset.
- Convert marker center from image space to machine space.
- Apply calibration parameters.
- Provide consistent coordinate transforms for both MVP and final tool.

### Inputs
- Marker center in image coordinates.
- Camera calibration parameters.
- Gantry position.

### Outputs
- Marker center in machine coordinates.

---

## 7. Configuration Module

### Purpose
Store and load all persistent settings.

### Responsibilities
- Camera parameters (resolution, exposure).
- Marker detection thresholds.
- Camera‑to‑laser offset.
- Simulator settings (MVP only).
- LightBurn bridge settings.

### Inputs
- Config file (JSON, YAML, or similar).

### Outputs
- Structured configuration objects.

---

## 8. Logging Module

### Purpose
Provide consistent logging across MVP and final tool.

### Responsibilities
- Log marker detection events.
- Log movement commands.
- Log LightBurn bridge state transitions.
- Log errors and warnings.

### Notes
- MVP: Python logging.
- Final: C++ logging framework (spdlog or Qt logging).

---

## 9. External Behaviour Contract

### Purpose
Ensure that MVP and final tool behave identically from the outside.

### Responsibilities
- Same marker detection semantics.
- Same Print & Cut state transitions.
- Same user confirmations.
- Same coordinate mapping behaviour.
- Same LightBurn integration logic.

---

## 10. Module Interactions (High-Level)

- **Camera → Recognizer**: provides frames.
- **Recognizer → UI**: provides marker detection results.
- **Recognizer → Simulator/Hardware**: triggers movement.
- **Simulator/Hardware → UI**: updates positions.
- **LightBurn Bridge → State Machine**: triggers marker selection events.
- **State Machine → Recognizer/Simulator**: coordinates Print & Cut flow.

---

## 11. MVP vs Final Tool Summary

| Module | MVP (Python) | Final Tool (C/C++/Qt) |
|--------|--------------|------------------------|
| Camera | DirectShow via OpenCV | DirectShow/Media Foundation |
| Recognizer | Python + OpenCV | C/C++ + OpenCV |
| Simulator | Yes | Optional |
| Bridge | Python WinAPI | Native WinAPI |
| UI | wxPython | Qt |
| Coordinates | Python | C/C++ |
| Config | Python | C/C++ |
| Logging | Python logging | spdlog / Qt logging |

---

This document defines the stable module boundaries for both MVP and final implementation.
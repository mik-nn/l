# Architecture

## 1. Overview

This project implements a marker-based alignment assistant for laser cutters that integrates with LightBurn’s Print & Cut workflow.  
The system is developed in two stages:

- **MVP:** Python tool using DirectShow + OpenCV and a simple UI.
- **Final tool:** Standalone C (or C++/Qt) application with the same external behaviour and protocols.

Core responsibilities:

- Detect custom markers in the camera field of view.
- Move camera/laser to the marker center (simulated first, then real).
- Cooperate with LightBurn Print & Cut using Alt+F1 and window focus.
- Provide a “camera-as-laser” simulator to visualize cut alignment on printed artwork.

---

## 2. Staged architecture

### 2.1 MVP architecture (Python)

**Goals:**

- Rapid experimentation with marker design and detection algorithms.
- Simulation of gantry and camera movement.
- Validation of the full Print & Cut flow with LightBurn.

**Main components:**

- **Camera module (Python + OpenCV + DirectShow):**
  - Opens the GigE camera via DirectShow.
  - Provides frames to the marker recognizer at a configurable FPS.
- **Marker recognizer (Python + OpenCV):**
  - Detects custom markers in the current frame.
  - Computes marker center and orientation.
  - Exposes a simple API: “marker found / not found”, “marker center in camera coordinates”.
- **Motion simulator:**
  - Simulates gantry X/Y movement and camera field of view over a virtual work area.
  - Simulates laser position relative to camera.
  - Allows “move camera to marker” and “move laser to marker center” operations.
- **LightBurn bridge (MVP):**
  - Detects the LightBurn main window (via PID + EnumWindows).
  - Hooks Alt+F1 when LightBurn is the active window.
  - Maintains a simple state machine: `idle → first_marker → second_marker`.
- **UI (wxPython or minimal custom UI):**
  - Shows camera image and overlays detected markers.
  - Shows “marker found / confirm” dialog.
  - Shows simulated laser/camera positions over a background image.

---

### 2.2 Final architecture (C / C++/Qt)

**Goals:**

- High performance and robustness.
- Standalone tool with a stable external contract.
- Same behaviour as the MVP, but implemented in native code.

**Main components:**

- **Core recognizer (C/C++):**
  - Marker detection implemented with OpenCV.
  - DirectShow-based camera capture.
  - Same detection semantics as the MVP (marker center, orientation, confidence).
- **Motion and device integration:**
  - Real gantry/laser movement instead of simulation.
  - Configurable mapping between camera coordinates and machine coordinates.
- **LightBurn bridge (native WinAPI):**
  - Native WinAPI hooks for Alt+F1 and window focus.
  - State machine for Print & Cut: first marker, second marker, ready.
- **UI (Qt):**
  - Modern UI for camera preview, overlays, and alignment visualization.
  - Optional simulator mode reusing the MVP concepts.

The final tool reuses the external behaviour and protocols defined and validated in the MVP.

---

## 3. Print & Cut workflow integration

### 3.1 User flow with LightBurn

1. User manually moves the **camera** (gantry) to the first printed marker.
2. When the marker enters the camera FOV, the tool:
   - Detects the marker.
   - Shows a confirmation UI: “Marker found, confirm?”.
3. After confirmation, the tool:
   - Computes the marker center.
   - Moves the **laser** to the marker center (real or simulated).
4. In LightBurn, the user:
   - Selects the corresponding marker.
   - Presses **Alt+F1** to register the first Print & Cut point.
5. The tool then:
   - Moves the camera to the second marker (or guides the user to do so).
   - Repeats detection and confirmation.
   - Moves the laser to the second marker center.
6. In LightBurn, the user:
   - Selects the second marker.
   - Presses the corresponding Print & Cut hotkey.
7. LightBurn completes its internal affine transform and proceeds with cutting.  
   The tool’s simulator shows where the cut will land on the printed image.

---

## 4. Modules

### 4.1 Camera module

- Uses DirectShow to access the GigE camera as a standard video device.
- Provides:
  - Current frame (RGB/gray).
  - Resolution and FOV configuration.
  - Frame timestamps (optional).

### 4.2 Marker recognizer

- Detects custom markers designed for high contrast and robustness.
- Outputs:
  - `found: bool`
  - `center: (x, y)` in image coordinates
  - `orientation` (optional)
  - `confidence` score
- Designed for frequent changes during MVP; final algorithms are ported to C/C++.

### 4.3 Motion simulator

- Represents:
  - Gantry X/Y coordinates.
  - Camera offset relative to laser.
  - Virtual work area with a background image (printed artwork + markers).
- Provides:
  - “Move camera to marker” operation.
  - “Move laser to marker center” operation.
  - Visualization of camera FOV and laser position.

### 4.4 LightBurn bridge

- Responsibilities:
  - Detect LightBurn main window.
  - Track when LightBurn is active.
  - Intercept Alt+F1 (and other Print & Cut hotkeys if needed).
  - Maintain Print & Cut state (first marker, second marker).
- In MVP, can be implemented in Python with WinAPI bindings; in the final tool, implemented natively.

### 4.5 UI layer

- Shows:
  - Live camera feed.
  - Marker overlays and status.
  - Simulated work area with camera and laser positions.
- Provides:
  - Confirmation dialogs for marker detection.
  - Simple controls for starting/stopping the Print & Cut assist flow.

---

## 5. Evolution: from MVP to final tool

1. **MVP phase (Python):**
   - Implement camera capture via DirectShow + OpenCV.
   - Implement basic marker detection and visualization.
   - Implement motion simulator and simple LightBurn bridge.
   - Iterate quickly on marker design and detection algorithms.

2. **Stabilization:**
   - Fix marker format and detection parameters.
   - Fix the external behaviour and states of the tool.
   - Document the user flow and module responsibilities.

3. **Final tool (C / C++/Qt):**
   - Port the stable marker detection logic to C/C++.
   - Implement native camera capture and WinAPI bridge.
   - Implement Qt UI and optional simulator mode.
   - Keep behaviour identical to the MVP where externally visible.

---

## 6. Documentation files

The following Markdown documents describe the system in more detail:

- `docs/architecture.md` — this file, high-level architecture and stages.
- `docs/modules.md` — detailed description of each module’s API and responsibilities.
- `docs/workflow-print-and-cut.md` — exact user flow with LightBurn and state transitions.
- `docs/markers.md` — marker design, detection assumptions, and constraints.
- `docs/simulator.md` — simulation model for camera, gantry, and laser.
- `docs/bridge-lightburn.md` — technical details of the LightBurn bridge (window detection, hooks, states).
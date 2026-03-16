# LaserCam Alignment Assistant

This project provides a marker-based alignment assistant for laser cutters that integrates with LightBurn's Print & Cut workflow. It uses a camera to detect printed markers on the work material, automatically moves the laser to the precise center of these markers, and helps the user register the alignment points in LightBurn, ensuring accurate cuts on pre-printed designs.

## Features

- **Real-time Camera Preview**: Shows a live feed from the camera.
- **Automatic Marker Detection**: Detects custom-designed markers on the print.
- **Automated Laser Positioning**: Moves the laser to the exact center of the detected markers.
- **Seamless LightBurn Integration**: Works with LightBurn’s Print & Cut workflow using standard hotkeys.
- **Two-Point Alignment**: Guides the user through a simple two-marker alignment process.
- **Simulator Mode**: A built-in simulator for development and testing without requiring physical hardware.

## Workflow

The tool streamlines the Print & Cut alignment process:

1.  **Print Artwork**: Print your design with two alignment markers included.
2.  **Position Material**: Place the printed material on the laser bed.
3.  **First Marker**: Manually move the camera/gantry so the first marker is visible in the camera view.
4.  **Detect & Align**: The tool detects the marker and automatically moves the laser to its center.
5.  **Confirm in LightBurn**: With the corresponding marker selected in LightBurn, press `Alt+F1` to set the first alignment point.
6.  **Second Marker**: Repeat the process for the second marker.
7.  **Cut**: LightBurn now has the correct alignment transform and can proceed with an accurate cut.

## Architecture

The project is developed in two main stages to ensure stability and performance:

1.  **MVP (Minimum Viable Product)**: A Python-based implementation for rapid prototyping, algorithm validation, and workflow simulation. It allows for quick iteration on marker design and detection logic.
2.  **Final Tool**: A standalone C/C++ application with a Qt-based UI. It ports the validated logic from the MVP to a high-performance, native application for production use.

Both implementations share the exact same external behavior and workflow, ensuring a consistent user experience.

## Technology Stack

| Component | MVP (Python) | Final Tool (C/C++/Qt) |
|---|---|---|
| **Language** | Python 3 | C/C++ |
| **UI** | wxPython or minimal | Qt |
| **Image Processing** | OpenCV | OpenCV |
| **Camera Capture**| DirectShow via OpenCV | Native DirectShow/Media Foundation |
| **LightBurn Bridge**| Python WinAPI bindings | Native WinAPI hooks |

## Project Structure

```
/
├── docs/             # Project documentation
├── mvp/              # Python MVP source code
├── final/            # C/C++/Qt final tool source code (planned)
├── markers/          # Marker design templates
├── simulator/        # Simulation assets
└── tests/            # Automated tests
```

## Core Modules

- **Camera Module**: Captures video from a DirectShow-compatible camera.
- **Marker Recognizer**: Detects markers in the camera feed.
- **Motion Simulator/Driver**: Simulates or controls gantry movement.
- **LightBurn Bridge**: Integrates with LightBurn by monitoring window focus and hotkeys.
- **Coordinate Mapping**: Translates coordinates between the camera, gantry, and laser.
- **UI Layer**: Provides visual feedback and user interaction.

---
For more detailed information, please refer to the documents in the `docs` directory.

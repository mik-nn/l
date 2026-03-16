# simulator.md — Camera and Gantry Simulation Model

This document describes the simulation environment used during the MVP phase. The simulator allows rapid development and testing of marker detection, coordinate mapping, and Print & Cut workflow without requiring real hardware.

## 1. Purpose of the Simulator

The simulator provides:
- a virtual gantry with X/Y coordinates,
- a virtual camera with a configurable field of view,
- a virtual laser offset relative to the camera,
- a virtual work area containing printed artwork and markers.

It enables testing of the entire workflow before hardware integration.

## 2. Components of the Simulator

The simulator consists of:
- a virtual work area image,
- a camera viewport that moves over the work area,
- a laser position derived from camera position and offset,
- a movement model for the gantry.

The simulator updates positions and renders overlays for debugging.

## 3. Camera Model

The camera model includes:
- resolution,
- field of view,
- pixel-to-millimeter scaling,
- optional lens distortion (ignored in MVP).

The camera viewport extracts a subregion of the work area image.

## 4. Gantry Model

The gantry model tracks:
- current X/Y position,
- movement commands,
- velocity and acceleration (simplified),
- boundaries of the work area.

The MVP uses instantaneous movement for simplicity.

## 5. Laser Offset

The laser is offset from the camera by a fixed vector.  
The simulator applies this offset to compute the laser position when the camera is centered on a marker.

## 6. Movement Operations

The simulator supports:
- move camera to marker,
- move laser to marker center,
- manual jogging via UI controls.

These operations mimic the behaviour of the final tool.

## 7. Visualization

The simulator renders:
- the work area,
- the camera viewport,
- detected markers,
- the laser position,
- movement paths.

This visualization is essential for debugging alignment logic.

## 8. Transition to Real Hardware

The simulator is removed or disabled in the final tool.  
The hardware driver replaces the movement model, but the external behaviour remains identical.
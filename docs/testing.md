# testing.md — Testing Strategy and Validation Approach

This document defines the testing methodology for the Marker Alignment Tool. It covers both the MVP (Python) and the final tool (C/C++/Qt), ensuring that behaviour remains consistent across implementations.

## 1. Testing Goals

The testing strategy ensures:

- correct marker detection,  
- correct coordinate mapping,  
- correct state machine transitions,  
- correct LightBurn integration behaviour,  
- correct simulation behaviour (MVP),  
- correct hardware behaviour (final tool),  
- consistent external behaviour across both layers.

## 2. MVP Testing

The MVP includes automated tests for:

- marker detection algorithms,  
- coordinate transforms,  
- simulator movement logic,  
- LightBurn bridge state transitions,  
- configuration loading,  
- UI-independent logic.

Tests are located in the tests/ directory.

## 3. Final Tool Testing

The final tool includes:

- unit tests for core logic,  
- integration tests for camera capture,  
- tests for hardware movement (mocked or simulated),  
- tests for WinAPI bridge behaviour,  
- UI tests where applicable.

The final tool must match the MVP’s behaviour exactly.

## 4. Test Summary Reporting

After running tests for complex tasks, the Agent must update docs/test-summary.md with:

- number of passed tests,  
- number of failed tests,  
- list of passed tests,  
- list of failed tests with error summaries.

This ensures traceability and reproducibility.

## 5. Manual Testing

Manual testing includes:

- verifying marker detection on real prints,  
- verifying alignment accuracy,  
- verifying LightBurn workflow,  
- verifying UI responsiveness,  
- verifying hardware safety.

Manual tests complement automated tests.

## 6. Behaviour Consistency Validation

The following behaviours must be validated across MVP and final tool:

- marker detection semantics,  
- coordinate mapping results,  
- state machine transitions,  
- LightBurn hotkey handling,  
- user-facing workflow.

Any deviation must be documented and corrected.

## 7. Regression Prevention

All bugs must include:

- a minimal reproducible test case,  
- a test added to prevent recurrence,  
- documentation updates if behaviour changes.

This ensures long-term stability.

## 8. Test Environment Requirements

The testing environment must include:

- a DirectShow-compatible camera (real or virtual),  
- LightBurn installed,  
- Windows 10 or later,  
- consistent configuration files.

The MVP may use simulated camera input for automated tests.
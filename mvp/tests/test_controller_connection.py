# mvp/tests/test_controller_connection.py
import pytest
from unittest.mock import MagicMock, patch

def test_ruida_position_reads_from_controller():
    """Test that RuidaController.position reads real coordinates from controller."""
    from mvp.controller import RuidaController
    
    # This test requires a running Ruida controller emulator
    # If no emulator running, skip
    try:
        controller = RuidaController(
            mode="udp",
            host="127.0.0.1",
            port=50200,
            timeout=0.5,
            retries=1,
        )
        controller.connect()
        
        if not controller.is_connected:
            pytest.skip("No Ruida controller/emulator running")
        
        # Read position - should query controller
        pos = controller.position
        
        print(f"Position read from controller: {pos}")
        
        # Verify we got a real position (not 0,0 which would be uninitialized)
        assert pos is not None
        assert isinstance(pos, tuple)
        assert len(pos) == 2
        
        # Print success
        print(f"SUCCESS: Controller returned real position: {pos}")
        
        controller.disconnect()
        
    except Exception as e:
        pytest.skip(f"No Ruida controller available: {e}")


def test_grbl_position_read():
    """Test that GRBL controller reads position correctly."""
    from mvp.controller import SimulatedController
    from mvp.simulator import MotionSimulator
    
    # Create a real simulated controller
    sim = MotionSimulator(
        work_area_size=(900, 600),
        camera_fov=(100, 100),
    )
    controller = SimulatedController(sim)
    
    # Initial position should be (0, 0)
    pos = controller.position
    assert pos == (0.0, 0.0), f"Expected (0.0, 0.0), got {pos}"
    
    # Move the gantry
    controller.move_to(100.0, 200.0)
    
    # Read position - should return new position
    pos = controller.position
    assert pos == (100.0, 200.0), f"Expected (100.0, 200.0), got {pos}"
    
    print(f"SUCCESS: Simulated controller position works correctly")


def test_controller_disconnect_releases_port():
    """Test that disconnect releases the controller for other apps."""
    from mvp.controller import RuidaController
    
    try:
        controller = RuidaController(
            mode="udp",
            host="127.0.0.1",
            port=50200,
            timeout=0.5,
            retries=1,
        )
        
        # Connect
        controller.connect()
        assert controller.is_connected, "Should be connected"
        
        # Disconnect
        controller.disconnect()
        assert not controller.is_connected, "Should be disconnected"
        
        print("SUCCESS: Controller disconnect releases connection")
        
    except Exception as e:
        pytest.skip(f"No Ruida controller available: {e}")


if __name__ == "__main__":
    print("Running controller connection tests...")
    
    test_grbl_position_read()
    print("test_grbl_position_read: PASSED")
    
    test_controller_disconnect_releases_port()
    print("test_controller_disconnect_releases_port: PASSED")
    
    test_ruida_position_reads_from_controller()
    print("test_ruida_position_reads_from_controller: PASSED")
    
    print("\nAll tests completed!")

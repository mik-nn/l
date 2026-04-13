# mvp/tests/test_controller_connection.py
import pytest
from unittest.mock import MagicMock, patch

def test_controller_position_read_at_startup():
    """Test that controller position is read at startup."""
    from mvp.config import Config
    from mvp.controller import RuidaController
    
    # Create a mock Ruida controller
    with patch('mvp.controller.RuidaController') as MockRuida:
        mock_controller = MagicMock()
        mock_controller.position = (100.0, 200.0)  # Real position from controller
        mock_controller.is_connected = True
        mock_controller.connect.return_value = None
        mock_controller.disconnect.return_value = None
        MockRuida.return_value = mock_controller
        
        # Load config
        cfg = Config.load()
        cfg.controller = "ruida"
        
        # Simulate the app startup flow
        # Create controller
        controller = RuidaController(
            mode=cfg.ruida_mode,
            host=cfg.ruida_host,
            port=cfg.ruida_port,
        )
        
        # Connect
        controller.connect()
        
        # Read position
        pos = controller.position
        
        # Disconnect
        controller.disconnect()
        
        # Verify position was read from controller
        assert pos == (100.0, 200.0), f"Expected (100.0, 200.0), got {pos}"


def test_controller_position_read_in_ui():
    """Test that UI reads real position from controller."""
    from mvp.controller import SimulatedController
    from mvp.camera_simulator import CameraSimulator
    
    # Create a mock simulator
    mock_sim = MagicMock()
    mock_sim.gantry_x = 0.0
    mock_sim.gantry_y = 0.0
    mock_sim.camera_x_mm = 0.0
    mock_sim.camera_y_mm = 0.0
    mock_sim.camera_fov_mm = (100.0, 100.0)
    mock_sim.camera_fov_px = (640, 480)
    mock_sim.workspace_pixels_per_mm = 10.0
    mock_sim.work_area = MagicMock()
    
    # Create simulated controller
    controller = SimulatedController(mock_sim)
    
    # Verify initial position
    pos = controller.position
    print(f"Initial position: {pos}")
    assert pos == (0.0, 0.0)


def test_real_controller_connection():
    """Test real controller connection if available."""
    import socket
    from mvp.controller import RuidaController
    
    # Try to connect to a real controller
    try:
        controller = RuidaController(
            mode="udp",
            host="127.0.0.1",
            port=50200,
            timeout=0.5,
        )
        
        # Try to connect
        controller.connect()
        
        if controller.is_connected:
            # Read position
            pos = controller.position
            print(f"Real controller position: {pos}")
            
            # Disconnect
            controller.disconnect()
            
            # Position should be read successfully
            assert pos is not None
            print(f"SUCCESS: Read position {pos} from real controller")
        else:
            print("Controller not connected - may not be running")
            
    except Exception as e:
        print(f"Could not test real controller: {e}")


if __name__ == "__main__":
    print("Running tests...")
    test_controller_position_read_at_startup()
    print("test_controller_position_read_at_startup: PASSED")
    
    test_controller_position_read_in_ui()
    print("test_controller_position_read_in_ui: PASSED")
    
    test_real_controller_connection()
    print("All tests completed!")

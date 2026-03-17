import sys
import importlib
from unittest.mock import MagicMock, patch
import pytest
import numpy as np

# Dummy classes to avoid MagicMock __init__ issues
class DummyTk:
    def __init__(self, *args, **kwargs): pass
    def title(self, title): pass
    def after(self, delay, callback): pass
    def mainloop(self): pass
    def protocol(self, name, func): pass
    def destroy(self): pass
    def bind(self, name, func): pass

class DummyFrame:
    def __init__(self, master=None, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass

class DummyCanvas:
    def __init__(self, master=None, *args, **kwargs): pass
    def pack(self, *args, **kwargs): pass
    def create_image(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass

# Use a fixture to mock tkinter and related modules for these tests
@pytest.fixture(autouse=True)
def mock_gui_dependencies():
    mock_tk_mod = MagicMock()
    mock_tk_mod.Tk = DummyTk
    mock_tk_mod.Frame = DummyFrame
    mock_tk_mod.Canvas = DummyCanvas
    mock_tk_mod.LEFT = "left"
    mock_tk_mod.RIGHT = "right"
    mock_tk_mod.NW = "nw"
    
    # Remove mvp modules from sys.modules to force re-import with mocks
    for mod in ['mvp.ui', 'mvp.app', 'mvp.camera', 'mvp.camera_simulator']:
        if mod in sys.modules:
            del sys.modules[mod]

    with patch.dict(sys.modules, {
        'tkinter': mock_tk_mod,
        'tkinter.ttk': MagicMock(),
        'PIL': MagicMock(),
        'PIL.Image': MagicMock(),
        'PIL.ImageTk': MagicMock(),
    }):
        yield

def test_ui_init():
    import mvp.ui
    mock_camera = MagicMock()
    with patch('mvp.ui.App.update'):
        app = mvp.ui.App(camera=mock_camera)
        assert app.camera == mock_camera

def test_ui_update():
    import mvp.ui
    mock_camera = MagicMock()
    frame = np.ones((100, 100, 3), dtype=np.uint8)
    mock_camera.get_frame.return_value = frame
    
    with patch('mvp.ui.App.after'): # Avoid infinite loop
        with patch('mvp.ui.ImageTk.PhotoImage') as mock_photo:
            with patch('mvp.ui.Image.fromarray'):
                app = mvp.ui.App(camera=mock_camera)
                # Clear mocks because they are called in __init__
                mock_camera.get_frame.reset_mock()
                
                app.update()
                
                mock_camera.get_frame.assert_called()
                assert mock_photo.called

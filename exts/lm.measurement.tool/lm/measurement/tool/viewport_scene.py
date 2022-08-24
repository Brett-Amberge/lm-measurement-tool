'''
Sets up the viewport and window
'''

import os
import omni.ui
from omni.ui import scene as sc
from omni.kit.window.toolbar import SimpleToolButton, WidgetGroup

# Import model and manipulator
from .ruler_model import RulerModel
from .ruler_manipulator import RulerManipulator

class MeasurementToolGroup(WidgetGroup):
    def __init__(self, icon_path, manipulator):
        super().__init__()
        self._icon_path = icon_path
        self._manipulator = manipulator

    def clean(self):
        super().clean()

    def get_style(self):
        style = {
            "Button.Image::ruler_button": {"image_url": f"{self._icon_path}/ruler_icon.png"},
        }
        return style

    def create(self, default_size):
        def on_clicked():
            self._manipulator.set_tool()

        button1 = omni.ui.ToolButton(
            name="ruler_button",
            tooltip="Enable measurement tool",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: on_clicked(),
        )

        return {"ruler_button": button1}

class ViewportScene:

    def __init__(self, viewport_window, ext_id: str):
        self._scene_view = None
        self._viewport_window = viewport_window

        # Create a unique frame for our scene view
        with self._viewport_window.get_frame(ext_id):
            # Create a default scene view
            self._scene_view = sc.SceneView()
            # Add the manipulator and model to the scene
            with self._scene_view.scene:
                self._manipulator = RulerManipulator(model=RulerModel())
            
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)
        
    # Functions for cleaning up the viewport
    def _del_(self):
        self.destroy()

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None


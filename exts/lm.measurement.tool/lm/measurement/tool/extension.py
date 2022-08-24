'''
Main extension file
'''

import os
import omni.ext 
import carb
import omni.kit.window.toolbar as tb
from omni.kit.viewport.utility import get_active_viewport_window
from carb.input import KeyboardInput as Key

from .viewport_scene import ViewportScene, MeasurementToolGroup

class MeasurementTool(omni.ext.IExt):

    def __init__(self):
        self._viewport_scene = None

    def on_startup(self, ext_id):
        print("[lm.measurement.tool] Measurement tool startup")

        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        icon_path = os.path.join(ext_path, "icons")

        # Get the active Viewport
        viewport_window = get_active_viewport_window()

        # Error if there is no Viewport
        if not viewport_window:
            carb.log_error(f"No viewport window to add {ext_id} scene to")
            return
        
        # Build out the scene
        self._viewport_scene = ViewportScene(viewport_window, ext_id)
        self._manipuator = self._viewport_scene._manipulator

        # Set up the toolbar
        self._toolbar = tb.get_instance()
        self._widget = MeasurementToolGroup(icon_path, self._manipuator)
        self._toolbar.add_widget(self._widget, -100)

    # Clean up
    def on_shutdown(self):
        self._toolbar.remove_widget(self._widget)
        self._widget.clean()
        self._widget = None
        self._toolbar = None

        if self._viewport_scene:
            self._viewport_scene.destroy()
            self._viewport_scene = None

        print("[lm.measurement.tool] Measurement Tool shutdown")
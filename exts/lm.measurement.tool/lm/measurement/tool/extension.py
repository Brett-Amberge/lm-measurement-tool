'''
Main extension file
'''

import omni.ext 
import carb
from omni.kit.viewport.utility import get_active_viewport_window

from .viewport_scene import ViewportScene

class MeasurementTool(omni.ext.IExt):

    def __init__(self):
        self._viewport_scene = None

    def on_startup(self, ext_id):
        print("[lm.measurement.tool] Measurement tool startup")

        # Get the active Viewport
        viewport_window = get_active_viewport_window()

        # Error if there is no Viewport
        if not viewport_window:
            carb.log_error(f"No viewport window to add {ext_id} scene to")
            return
        
        # Build out the scene
        self._viewport_scene = ViewportScene(viewport_window, ext_id)

    def on_shutdown(self):
        if self._viewport_scene:
            self._viewport_scene.destroy()
            self._viewport_scene = None
        print("[lm.measurement.tool] Measurement Tool shutdown")
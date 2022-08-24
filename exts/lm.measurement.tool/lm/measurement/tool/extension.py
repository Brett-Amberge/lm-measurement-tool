'''
Main extension file
'''

import os
import omni.ext 
import carb
import omni.kit.window.toolbar as tb
from omni.kit.viewport.utility import get_active_viewport_window
from omni.kit.window.toolbar import SimpleToolButton, WidgetGroup
from carb.input import KeyboardInput as Key

from .viewport_scene import ViewportScene

class MeasurementToolGroup(WidgetGroup):
    def __init__(self, icon_path):
        super().__init__()
        self._icon_path = icon_path

    def clean(self):
        super().clean()

    def get_style(self):
        style = {
            "Button.Image::ruler_button": {"image_url": f"{self._icon_path}/ruler_icon.png"},
        }
        return style

    def create(self, default_size):
        def on_clicked():
            toolbar = tb.get_instance()
            button = toolbar.get_widget("scale_op")
            if button is not None:
                button.enabled = not button.enabled

        button1 = omni.ui.ToolButton(
            name="ruler_button",
            tooltip="Enable measurement tool",
            width=default_size,
            height=default_size,
            mouse_pressed_fn=lambda x, y, b, _: on_clicked(),
        )

        return {"ruler_button": button1}

class MeasurementTool(omni.ext.IExt):

    def __init__(self):
        self._viewport_scene = None

    def on_startup(self, ext_id):
        print("[lm.measurement.tool] Measurement tool startup")

        ext_path = omni.kit.app.get_app().get_extension_manager().get_extension_path(ext_id)
        icon_path = os.path.join(ext_path, "icons")

        # Set up the toolbar
        self._toolbar = tb.get_instance()
        self._widget = MeasurementToolGroup(icon_path)
        self._toolbar.add_widget(self._widget, -100)

        # Get the active Viewport
        viewport_window = get_active_viewport_window()

        # Error if there is no Viewport
        if not viewport_window:
            carb.log_error(f"No viewport window to add {ext_id} scene to")
            return
        
        # Build out the scene
        self._viewport_scene = ViewportScene(viewport_window, ext_id)

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
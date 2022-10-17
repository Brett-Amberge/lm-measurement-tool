'''
Sets up the viewport and window.
Adds the tool options to the tool bar.
'''

import omni.ui
from omni.ui import scene as sc
from omni.kit.window.toolbar import WidgetGroup

# Import model and manipulator
from .ruler_model import RulerModel
from .ruler_manipulator import RulerManipulator

# Toolbar button widget group
class MeasurementToolGroup(WidgetGroup):

    # Constructor
    def __init__(self, icon_path, manipulator):
        super().__init__()
        self._icon_path = icon_path
        self._manipulator = manipulator

    # Clean up the toolbar when the extension is disabled
    def clean(self):
        super().clean()

    # Retrieve the icon images
    def get_style(self):
        style = {
            "Button.Image::ruler_button": {"image_url": f"{self._icon_path}/ruler_icon.png"},
            "Button.Image::compass_button": {"image_url": f"{self._icon_path}/compass_icon.png"},
        }
        return style

    # Setup the UI buttons and add funtionality.
    def create(self, default_size):

        # Activate the appropriate manipulator tool when a button is pressed.
        def on_clicked(btn):
            self._manipulator.set_tool(btn)

        button1 = omni.ui.ToolButton(
            name="ruler_button",
            tooltip="Enable ruler tool",
            width=default_size,
            height=default_size,
            checked=False,
            mouse_pressed_fn=lambda x, y, b, _: on_clicked("RULER"),
        )

        button2 = omni.ui.ToolButton(
            name="compass_button",
            tooltip="Enable compass tool",
            width=default_size,
            height=default_size,
            checked=False,
            #mouse_pressed_fn=lambda x, a, b, _: on_clicked("ANGLE"),
        )

        return {"ruler_button": button1, "compass_button": button2}

# Viewport Scene class, adds the manipulator to the active viewport window
class ViewportScene:

    # Contstructor
    def __init__(self, viewport_window, ext_id: str):
        self._scene_view = None
        self._viewport_window = viewport_window

        # Create a unique frame for our scene view
        with self._viewport_window.get_frame(ext_id):
            # Create a default scene view
            self._scene_view = sc.SceneView()
            # Add the manipulator to the scene
            with self._scene_view.scene:
                # Create a new model object and point the manipulator to it
                self._manipulator = RulerManipulator(model=RulerModel(), scene_view=self._scene_view)
            
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


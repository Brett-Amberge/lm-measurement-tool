from omni.ui import scene as sc

# Import model and manipulator
from .ruler_model import RulerModel
from .ruler_manipulator import RulerManipulator

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
                RulerManipulator(model=RulerModel())
            
            self._viewport_window.viewport_api.add_scene_view(self._scene_view)
        
    def _del_(self):
        self.destroy()

    def destroy(self):
        if self._scene_view:
            # Empty the SceneView of any elements it may have
            self._scene_view.scene.clear()
            # Be a good citizen, and un-register the SceneView from Viewport updates
            if self._viewport_window:
                self._viewport_window.viewport_api.remove_scene_view(self._scene_view)
        # Remove our references to these objects
        self._viewport_window = None
        self._scene_view = None


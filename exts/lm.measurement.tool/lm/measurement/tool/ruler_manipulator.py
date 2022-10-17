'''
Set up the gestures in the viewport and update the model when one occurs.
Draws the ruler in the scene based on the model.
'''

import weakref
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.kit
import omni.appwindow
import omni.usd
import carb
import omni.kit.viewport_legacy as vp
from enum import Enum
from pxr import UsdGeom, Gf, Usd
from omni.kit.viewport.utility import get_active_viewport_window
from omni import ui

from .ruler_model import RulerModel
from .mesh_raycast import MeshRaycast

# What tool is currently active
class ToolType(Enum):
    DISABLED = 0
    RULER = 1
    ANGLE = 2

# Gesture manager to give precendence to certain gestures
class Manager(sc.GestureManager):
    def __init__(self):
        super().__init__()

    def should_prevent(self, gesture, preventer):
        if preventer._name == "Double": # Double click always takes precedence
            return True

mgr = Manager()

# Left click gesture to start measurement
class _ClickGesture(sc.ClickGesture):
    def __init__(self, manipulator: sc.Manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = "Left"
        self._start = False
        self.__manipulator = manipulator
        self._manager = mgr

    def on_ended(self):
        # Update the line whenever a click happens
        if self.__manipulator._tool.value == 1: # Check if the ruler tool is enabled
            self._start = not self._start
            model = self.__manipulator.model
            point = self.__manipulator.click_ray()
            if point:
                print(point)
                model.add_point(point)
                self.__manipulator.invalidate() # Redraw the line
            else:
                print("[lm.measurement.tool] No mesh at this point")

# Double click gesture to clear any active measurements
class _DoubleClickGesture(sc.DoubleClickGesture):
    def __init__(self, manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = "Double"
        self.__manipulator = manipulator
        self._manager = mgr

    def on_ended(self):
        # Clear the list of points and remove the lines on double click
        if self.__manipulator._tool.value == 1: # Check if the ruler tool is enabled
            model = self.__manipulator.model
            model.clear_points()
            self.__manipulator.invalidate()

# Ruler Manipulator class, add the gestures to the screen and draw measurement lines from the model, if any
class RulerManipulator(sc.Manipulator):

    # Constructor
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.gestures = []

        self._tool = ToolType.DISABLED
        self._active = False

        self._viewport = omni.kit.viewport_legacy.get_viewport_interface()
        self._mr = MeshRaycast()
        self.viewport_window = get_active_viewport_window()
        self._viewport_window = self._viewport.get_viewport_window()
        
        self._usd_context = self._get_context()

        # Set up a carb input interface to listen for mouse events
        self._input = carb.input.acquire_input_interface()
        self._input_sub_id = None

        self.mx = 0
        self.my = 0

    # Set up the tool when its enabled
    def _start(self):
        # Disable object selection in the viewport
        self._viewport_window.set_enabled_picking(False)

        # Register input events
        self._input_sub_id = self._input.subscribe_to_input_events(self._on_input_event, order=-10000)

    # Clean up the tool when its disabled
    def _stop(self):
        # Re-enable object selection in the viewport
        self._viewport_window.set_enabled_picking(True)

        # Clear out the model and start anew
        self.model.clear_points()
        self.invalidate()

        # Unregister input events
        if self._input_sub_id is not None:
            self._input.unsubscribe_to_input_events(self._input_sub_id)
            self._input_sub_id = None

    # Toggle the tool between active and inactive states
    def set_active(self, active):
        if self._active == active:
            return
        self._active = active
        if active:
            self._start()
        else:
            self._stop()

    # Get the current USD context we are attached to
    def _get_context(self) -> Usd.Stage:
        return omni.usd.get_context()

    # Process abstract input events
    def _on_input_event(self, event, *_):
        # Listen for mouse events, return on anything else
        if event.deviceType == carb.input.DeviceType.MOUSE:
            return self._on_global_mouse_event(event.event)
        else:
            return True

    # Process any mouse events
    def _on_global_mouse_event(self, event, *_):
        # Get the screen position of a left click event
        if event.type == carb.input.MouseEventType.LEFT_BUTTON_DOWN:
            # Return the x,y coords as normalized coords between 0 and 1
            x,y = self._get_position_in_viewport(event.normalized_coords)
            if x is None or y is None:
                return True

            self._update_mouse_position(x, y)

    # Update mouse position variables
    def _update_mouse_position(self, x, y):
        self.mx = x
        self.my = y

    # Get the relative mouse position within the acitve viewport
    def _get_position_in_viewport(self, coords):
        if coords.x < 0.0 or coords.x > 1.0 or coords.y < 0.0 or coords.y > 1.0:
            return (None, None)

        viewport_window = self._viewport_window
        if not viewport_window:
            return (None, None)

        # In kit, there may be a tab bar
        tab_bar_height = 22 if viewport_window.dock_tab_bar_visible else 0

        # Dock splitter is different between kit and view
        window_title = carb.settings.get_settings().get("/app/window/title")
        if window_title is not None and window_title == "Omniverse View":
            dock_splitter_size = 0
        else:
            dock_splitter_size = 4

        # Remove dock splitter and tab bar from viewport window size
        width = viewport_window.width - dock_splitter_size * 2
        height = viewport_window.height - dock_splitter_size * 2 - tab_bar_height

        # Get screen position relative to the main window
        x = coords.x * width + viewport_window.position_x + dock_splitter_size
        y = coords.y * height + viewport_window.position_y + dock_splitter_size + tab_bar_height

        # Get valid viewport texture area
        rect = self._viewport_window.get_viewport_rect()

        # Calculate the dimensions of the viewport rectangle
        rect_w = float(rect[2] - rect[0])
        rect_h = float(rect[3] - rect[1])
        if rect_w / rect_h > width / height:
            rect_h = rect_h / rect_w * width
            rect_w = width
            h_diff = (height - rect_h) * 0.5
            rect = [0, h_diff, width, height - h_diff]
        else:
            rect_w = rect_w / rect_h * height + dock_splitter_size * 2
            rect_h = height
            w_diff = (width - rect_w) * 0.5
            rect= [w_diff, 0, width - w_diff, height]

        # Calculate relative x,y position based on screen size
        x = coords.x * width
        y = coords.y * height

        # Return if relative x,y is outside of viewport rectangle
        if x < rect[0] or y < rect[1] or x > rect[2] or y > rect[3]:
            return (None, None)

        # Calculate mouse position in viewport rectangle
        mx = (x - rect[0]) / (rect[2] - rect[0])
        my = (y - rect[1]) / (rect[3] - rect[1])
        mx = mx * 2.0 - 1.0
        my = -(my * 2.0 - 1.0)

        return (mx, my)

    # Return click position as a tuple
    def get_mouse_pos(self):
        return (self.mx, self.my)

    # Called when the manipulator is constructed or invalidated by a model update.
    # Sets up any screen gestures and draws measurements lines if any exist.
    def on_build(self):

        # Create a new model if one does not already exist
        if not self.model:
            self.model = RulerModel()

        # Set the gesture(s) on the screen
        sc.Screen(gestures=self.gestures or [_ClickGesture(weakref.proxy(self)), _DoubleClickGesture(weakref.proxy(self))])

        # Draw the measurement lines
        self._draw_shape()

        # Set up labels above the lines to show the distance between the two endpoints
        points = self.model.get_value(self.model.get_item('points'))
        for i in range(len(points) - 1):
        # Position the distance labels above the center of the lines
            position = self.model.get_midpoint(points[i], points[i+1])
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0,5,0)):
                            sc.Label(f"{self.model.calculate_dist(points[i], points[i+1])} cm", alignment=ui.Alignment.CENTER_BOTTOM, size=20)

    # Method called when a click event occurs.
    # Creates a new measurement line point based on raycast from mouse click to nearest object in the scene.
    # TODO Ensure the mouse coordinates and measurement lines are accurate to world space
    def click_ray(self):
        pos = self.get_mouse_pos()
        #api = self.viewport_window.viewport_api

        model = self.scene_view.model   # Get the current camera model
        proj = model.projection         # Get camera projection matrix
        invProj = proj.get_inverse()    # Invert projection matrix for camera coords
        view = model.view               # Get camera view matrix
        invView = view.get_inverse()    # Invert view matrix for world coords

        # Get the position of the camera in world coordinates
        worldCam = Gf.Vec4d(invView[12], invView[13], invView[14], 1)

        # Convert the mouse click to homogeneous coords
        position = Gf.Vec4d(pos[0] * worldCam[2], pos[1] * worldCam[2], 1, 1)

        # Convert to Gf matrices to make the math easier
        p = Gf.Matrix4d(*invProj)
        v = Gf.Matrix4d(*invView)

        camPos = position * p           # Convert the position to homogeneous camera coords
        wrldPos = camPos * v            # Convert from homogeneous camera to homogeneous world
        print(wrldPos)
        # Divide by w to get the position in world coordinates
        origin = (wrldPos[0] + worldCam[0], wrldPos[1] + worldCam[1], wrldPos[2] + worldCam[2])
        print(origin)

        # Find the camera's forward vector
        camFor = Gf.Vec3d(invView[8], invView[9], invView[10])

        rayDist = 1000000000            # Pew pew
        # get_inverse returns the forward vector in eye coords, need to flip it to face forward
        # Fire a ray from the mouse to look for intersection with any scene objects
        hit = self._mr.raycast_closest(origin, -camFor, rayDist)
        hit_pos = False
        if hit["hit"]:
            # If the ray intersects with an object, store the position of the intersection in world coords
            print("[lm.measurement.tool] Hit!")
            dist = hit.get("distance", 1.0)
            if dist > 0:
                hit_pos = [hit["position"][0], hit["position"][1], hit["position"][2]]

        return hit_pos

    # Called when a value in the model is changed and _item_changed is called
    def on_model_updated(self, item):
        # Update the line based on the model
        self.invalidate()

    # Draw the line based on any points stored in the model
    def _draw_shape(self):
        if not self.model:
            return
        points = self.model.get_value(self.model.get_item('points'))
        if len(points) > 1:
            # Curve allows for more than one active measurement at a time
            sc.Curve(points, curve_type=sc.Curve.CurveType.LINEAR)

    # Toggle the tool on or off using input from toolbar buttons
    # TODO Make tool states exclusive (i.e. only line or angle measure active at a time, not both at once)
    def set_tool(self, tool):
        if self._tool.value > 0:
            self._tool = ToolType.DISABLED
            self.set_active(False)
        else:
            if tool == "RULER":
                self._tool = ToolType.RULER
                self.set_active(True)
            """if tool == "ANGLE":
                self._tool = ToolType.ANGLE"""

        
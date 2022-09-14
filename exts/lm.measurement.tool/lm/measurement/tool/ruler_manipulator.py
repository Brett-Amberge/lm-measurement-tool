'''
Update the view and model when user input occurs
'''

import weakref
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.kit
import omni.ui as ui
import omni.appwindow
from enum import Enum
from pxr import UsdGeom, Gf, Usd
from omni.kit.viewport.utility import get_active_viewport_window

from .ruler_model import RulerModel
from .mesh_raycast import MeshRaycast

class ToolType(Enum):
    DISABLED = 0
    RULER = 1
    ANGLE = 2

class Manager(sc.GestureManager):
    def __init__(self):
        super().__init__()

    def should_prevent(self, gesture, preventer):
        if preventer._name == "Double": # Double click always takes precedence
            return True

mgr = Manager()

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
            point = self.sender.gesture_payload.mouse
            point = self.__manipulator.click_ray(point)
            if point:
                model.add_point(point)
                self.__manipulator.invalidate() # Redraw the line
            else:
                print("[lm.measurement.tool] No mesh at this point")

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

class RulerManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gestures = []
        self._tool = ToolType.DISABLED
        self.viewport_window = get_active_viewport_window()
        self._usd_context = omni.usd.get_context()
        self._viewport = omni.kit.viewport_legacy.get_viewport_interface()
        self._mr = MeshRaycast()

    def on_build(self):
        if not self.model:
            self.model = RulerModel()

        # Set the gesture(s) on the screen
        sc.Screen(gestures=self.gestures or [_ClickGesture(weakref.proxy(self)), _DoubleClickGesture(weakref.proxy(self))])

        self._draw_shape()

        points = self.model.get_value(self.model.get_item('points'))
        for i in range(len(points) - 1):
        # Position the distance labels above the center of the lines
            position = self.model.get_midpoint(points[i], points[i+1])
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0,5,0)):
                            sc.Label(f"{self.model.calculate_dist(points[i], points[i+1])} cm", alignment=ui.Alignment.CENTER_BOTTOM, size=20)

    def click_ray(self, position):
        pos = Gf.Vec3d(*position, 0)
        view_mat = self.scene_view.view # Get camera view matrix
        inv = view_mat.get_inverse()    # Invert view matrix for world coords
        api = self.viewport_window.viewport_api
        origin = api.ndc_to_world.Transform(pos * 425)

        rayDist = 1000000000
        rayDir = Gf.Vec3d(inv[8], inv[9], inv[10])
        # get_inverse returns the forward vector in eye coords, need to flip it to face forward
        hit = self._mr.raycast_closest(origin, -rayDir, rayDist)
        hit_pos = False
        if hit["hit"]:
            print("[lm.measurement.tool] Hit!")
            dist = hit.get("distance", 1.0)
            if dist > 0:
                hit_pos = [hit["position"][0], hit["position"][1], hit["position"][2]]

        return hit_pos

    def on_model_updated(self, item):
        # Update the line based on the model
        self.invalidate()
        self._draw_shape()

    def _draw_shape(self):
        # Draw the line based on the start and end point stored in the model
        if not self.model:
            return
        points = self.model.get_value(self.model.get_item('points'))
        if len(points) > 1:
            with sc.Transform(scale_to=sc.Space.WORLD):
                sc.Curve(points, curve_type=sc.Curve.CurveType.LINEAR)

    def set_tool(self, tool):
        # Toggle the tool on or off
        if self._tool.value > 0:
            self._tool = ToolType.DISABLED
        else:
            if tool == "RULER":
                self._tool = ToolType.RULER
            if tool == "ANGLE":
                self._tool = ToolType.ANGLE

        
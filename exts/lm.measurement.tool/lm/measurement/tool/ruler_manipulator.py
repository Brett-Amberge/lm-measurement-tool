'''
Update the view and model when user input occurs
'''

import weakref
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.kit
import omni.kit.commands
import omni.ui as ui
from enum import Enum

from .ruler_model import RulerModel

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
        if self.__manipulator._tool.value > 0: # Check if the ruler tool is enabled
            self._start = not self._start
            model = self.__manipulator.model
            point = self.sender.gesture_payload.ray_closest_point

            model.add_point(point)
            model.calculate_dist(model.points[0], model.points[-1])
            self.__manipulator.invalidate() # Redraw the line

class _DoubleClickGesture(sc.DoubleClickGesture):
    def __init__(self, manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = "Double"
        self.__manipulator = manipulator
        self._manager = mgr

    def on_ended(self):
        # Clear the list of points and remove the lines on double click
        model = self.__manipulator.model
        model.clear_points()
        self.__manipulator.invalidate()

class RulerManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gestures = []
        self._tool = ToolType.DISABLED

    def on_build(self):
        if not self.model:
            self.model = RulerModel()

        # Set the gesture(s) on the screen
        sc.Screen(gestures=self.gestures or [_ClickGesture(weakref.proxy(self)), _DoubleClickGesture(weakref.proxy(self))])

        self._draw_shape()

        points = self.model.points
        for i in range(len(points) - 1):
        # Position the distance labels above the center of the lines
            position = self.model.get_midpoint(points[i], points[i+1])
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0,5,0)):
                            sc.Label(f"{self.model.calculate_dist(points[i], points[i+1])}", alignment=ui.Alignment.CENTER_BOTTOM, size=20)
        

    def on_model_updated(self, item):
        # Update the line based on the model
        if self.model.points:
            self._draw_shape()

    def _draw_shape(self):
        # Draw the line based on the start and end point stored in the model
        if not self.model:
            return
        if self.model.points:
            i = 0
            points = self.model.points
            while i < (len(points) - 1):
                sc.Line(points[i], points[i+1])
                i += 1

    def set_tool(self):
        # Toggle the tool on or off
        if self._tool.value == 0:
            self._tool = ToolType.RULER
        else:
            self._tool = ToolType.DISABLED

        
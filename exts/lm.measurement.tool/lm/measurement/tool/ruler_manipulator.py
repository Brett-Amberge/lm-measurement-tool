'''
Update the view and model when user input occurs
'''

import weakref
from omni.ui import scene as sc
from omni.ui import color as cl
import omni.kit
import omni.kit.commands
import omni.ui as ui

from .ruler_model import RulerModel

class _ClickGesture(sc.ClickGesture):
    def __init__(self, manipulator: sc.Manipulator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start = False
        self.__manipulator = manipulator

    def on_ended(self):
        # Update the line whenever a click happens
        self._start = not self._start
        model = self.__manipulator.model
        point = self.sender.gesture_payload.ray_closest_point

        if self._start:
            model.set_floats(model.startpoint, point)
        else:
            model.set_floats(model.endpoint, point)
            model.calculate_dist()
            self.__manipulator.invalidate() # Redraw the line

class RulerManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gestures = []

    def on_build(self):
        if not self.model:
            self.model = RulerModel()

        # Set the gesture on the screen
        sc.Screen(gestures=self.gestures or [_ClickGesture(weakref.proxy(self))])

        self._draw_shape()

        # Position the distance label above the center of the line
        if self.model.dist.value > 0.0:
            position = self.model.get_midpoint()
            with sc.Transform(transform=sc.Matrix44.get_translation_matrix(*position)):
                with sc.Transform(look_at=sc.Transform.LookAt.CAMERA):
                    with sc.Transform(scale_to=sc.Space.SCREEN):
                        with sc.Transform(transform=sc.Matrix44.get_translation_matrix(0,5,0)):
                            sc.Label(f"{self.model.dist.value}", alignment=ui.Alignment.CENTER_BOTTOM, size=20)
        

    def on_model_updated(self, item):
        # Update the line based on the model
        if item == self.model.startpoint or item == self.model.endpoint:
            self._draw_shape()

    def _draw_shape(self):
        # Draw the line based on the start and end point stored in the model
        if not self.model:
            return
        if self.model.startpoint and self.model.endpoint:
            sc.Line(self.model.startpoint.value, self.model.endpoint.value)

        
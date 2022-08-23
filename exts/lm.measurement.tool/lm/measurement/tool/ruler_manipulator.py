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
        self.start = False
        self.__manipulator = manipulator

    def on_ended(self):
        self.start = not self.start
        model = self.__manipulator.model
        point = self.sender.gesture_payload.ray_closest_point

        if self.start:
            model.set_floats(model.startpoint, point)
        else:
            model.set_floats(model.endpoint, point)
            model.calculate_dist()
            self.__manipulator.invalidate()

class RulerManipulator(sc.Manipulator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gestures = []

    def on_build(self):
        if not self.model:
            self.model = RulerModel()

        self._draw_shape()

        sc.Screen(gestures=self.gestures or [_ClickGesture(weakref.proxy(self))])

    def on_model_updated(self, item):
        if item == self.model.startpoint or item == self.model.endpoint:
            self._draw_shape()

    def _draw_shape(self):
        if not self.model:
            return
        if self.model.startpoint and self.model.endpoint:
            sc.Line(self.model.startpoint.value, self.model.endpoint.value)
            sc.Label(str(self.model.dist.value), alignment=ui.Alignment.RIGHT_BOTTOM, color=cl.white, size=50)
        
from math import sqrt
from omni.ui import scene as sc
from pxr import Usd, UsdGeom, Tf, Gf
import omni.usd
import carb

class RulerModel(sc.AbstractManipulatorModel):

    # Subclasses for storing model information
    class PositionItem(sc.AbstractManipulatorItem):
        def __init__(self):
            super().__init__()
            self.value = [0,0,0]

    class FloatItem(sc.AbstractManipulatorItem):
        def __init__(self):
            super().__init__()
            self.value = 0.0

    def __init__(self):
        super().__init__()
        self.startpoint = RulerModel.PositionItem()
        self.endpoint = RulerModel.PositionItem()
        self.dist = RulerModel.FloatItem()

    def get_as_floats(self, item):
        # Return the value of the given item
        return item.value

    def set_floats(self, item, value):
        # Change the value of the given item
        item.value = value
        self._item_changed(item) # Tells the manipulator the model changed

    def calculate_dist(self):
        # Find the distance between the two points
        x1,y1,z1 = self.startpoint.value
        x2,y2,z2 = self.endpoint.value

        distance = round(sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2), 3)

        self.set_floats(self.dist, distance)
    
    def get_midpoint(self):
        # Find the middle of the line
        x1,y1,z1 = self.startpoint.value
        x2,y2,z2 = self.endpoint.value

        midpoint = [(x2+x1)/2, (y2+y1)/2, (z2+z1)/2]
        #print(str(self.startpoint.value) +  " " + str(midpoint) + " " + str(self.endpoint.value))
        return midpoint

        


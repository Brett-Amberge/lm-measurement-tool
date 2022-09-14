'''
Stores details about the line
'''

from math import sqrt
from omni.ui import scene as sc

class RulerModel(sc.AbstractManipulatorModel):

    # Absctract container class(es)
    class ListItem(sc.AbstractManipulatorItem):
        def __init__(self, value=[]):
            self.value = value

    def __init__(self):
        super().__init__()
        self._points = RulerModel.ListItem()

    # Find the distance between the two points
    def calculate_dist(self, startpoint, endpoint):
        x1,y1,z1 = startpoint
        x2,y2,z2 = endpoint

        distance = round(sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2), 3)

        return distance
    
    # Find the midpoint between the two points
    def get_midpoint(self, startpoint, endpoint):     
        x1,y1,z1 = startpoint
        x2,y2,z2 = endpoint

        midpoint = [(x2+x1)/2, (y2+y1)/2, (z2+z1)/2]

        return midpoint

    # Accessor methods
    def get_item(self, item):
        if item == 'points':
            return self._points

    def get_value(self, item):
        if item == self._points:
            return self._points.value

    # Mutator methods
    def add_point(self, point):
        self.get_value(self.get_item('points')).append(point)
        #self._item_changed(self._points)

    def clear_points(self):
        self.get_value(self.get_item('points')).clear()
        #self._item_changed(self._points)
        


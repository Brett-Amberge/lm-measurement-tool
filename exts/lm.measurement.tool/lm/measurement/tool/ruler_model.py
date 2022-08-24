'''
Stores details about the line
'''

from math import sqrt
from omni.ui import scene as sc
from pxr import Usd, UsdGeom, Tf, Gf
import omni.usd
import carb

class RulerModel(sc.AbstractManipulatorModel):

    def __init__(self):
        super().__init__()
        self.points = []

    def add_point(self, point):
        self.points.append(point)

    def clear_points(self):
        self.points.clear()

    def calculate_dist(self, startpoint, endpoint):
        # Find the distance between the two points
        x1,y1,z1 = startpoint
        x2,y2,z2 = endpoint

        distance = round(sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2), 3)

        return distance
    
    def get_midpoint(self, startpoint, endpoint):
        # Find the midpoint between the two points
        x1,y1,z1 = startpoint
        x2,y2,z2 = endpoint

        midpoint = [(x2+x1)/2, (y2+y1)/2, (z2+z1)/2]
        #print(str(self.startpoint.value) +  " " + str(midpoint) + " " + str(self.endpoint.value))
        return midpoint

        


from PyQt6.QtCore import *
from PyQt6.QtGui import *

class Polygon(QPolygonF):
    def __init__(self, bbox=None, id=0, simplified_pol=None, classified=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.bbox = bbox
        self.simplified_pol = simplified_pol
        self.classified = classified

    def addVertex(self, vertex):
        self.append(vertex)
        
    def addQPolygonF(self, pol:QPolygonF):
        for point in pol:
            self.addVertex(point)

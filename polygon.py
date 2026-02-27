from PyQt6.QtCore import *
from PyQt6.QtGui import *

class Polygon(QPolygonF):
    def __init__(self, id=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id

    def addVertex(self, vertex):
        self.append(vertex)

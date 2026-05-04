from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from edge import *


class Contour(Edge):
    def __init__(self, p1, p2, z):
        super().__init__(p1, p2)
        self.__z = z
        
    def z(self):
        return self.__z
    
    def __hash__(self):
        return hash((
            self.getStart().x(), self.getStart().y(),
            self.getEnd().x(), self.getEnd().y(),
            self.z()
        ))
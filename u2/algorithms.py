from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *

class Algorithms:
    
    def __init__(self):
        pass
    
    def get2LinesAngle(self, p1, p2, p3, p4):
        #Calculates the angle between two lines
        
        #Vector u
        ux = p2.x() - p1.x()
        uy = p2.y() - p1.y()
        
        #Vector v
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()
        
        #Dot product
        dot = ux * vx + uy * vy
                
        #Norms
        norm_u = sqrt(ux**2 + uy**2)
        norm_v = sqrt(vx**2 + vy**2)
        
        #Compute phi
        phi = acos(dot / (norm_u * norm_v))
        
        return phi
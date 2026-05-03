from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *

class Triangle:
    def __init__(self, p1:QPoint3DF, p2:QPoint3DF, p3:QPoint3DF):
        
        self.__aspect = 0
        self.__slope = 0

        #Add points
        self.__p1 = p1
        self.__p2 = p2
        self.__p3 = p3
    
    
    def getP1(self):
        return self.__p1
    
    
    def getP2(self):
        return self.__p2
    
    
    def getP3(self):
        return self.__p3
    
    
    def getAspect(self):
        return self.__aspect
    
    
    def getSlope(self):
        return self.__slope
    
    
    def setAspect(self, aspect):
        self.__aspect = aspect
    
    
    def setSlope(self, slope):
        self.__slope = slope
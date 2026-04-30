from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from random import *
from math import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__points =[]
        self.__DT = []
        self.__contours = []
        self.__triangles = []
        self.__view_DT = True
        self.__view_Slope = True
        self.__view_Aspect = True
        self.__view_Contours = True
        
        
    def mousePressEvent(self, e):
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Get random z
        z_min = 200
        z_max = 600
        z = random() * (z_max - z_min) + z_min

        #Create new point
        p = QPoint3DF(x, y, z)
        
        #Add P to polygon
        self.__points.append(p)
        
        #Repaint
        self.repaint()
        

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #Create new pen
        pen = QPen()
        
        #Draw slope
        if self.__view_Slope:
            #Set properties, triangles, slope
            pen.setColor(Qt.GlobalColor.black)
            qp.setPen(pen)

            #Process all triangles
            for triangle in self.__triangles:
                
                #Get slope
                slope = triangle.getSlope()

                #Rescale aspect to 0-255
                k = (2*255) / pi
                gray = int(255 - (slope * k))

                #Create Qt Color
                color = QColor(gray, gray, gray)

                #Assign brush color
                qp.setBrush(color)

                #Draw polygon
                pol = QPolygonF([triangle.getP1(), triangle.getP2(), triangle.getP3()])
                
                qp.drawPolygon(pol)
            
        #Draw DT
        if self.__view_DT:
            #Set properties, edges
            pen.setColor(Qt.GlobalColor.green)
            qp.setPen(pen)
            
            #Draw edges
            for e in self.__DT:
                qp.drawLine(e.getStart(), e.getEnd())

        #Draw contour lines
        if self.__view_Contours:        
            #Set properties, contours
            pen.setColor(QColor(85, 38, 0)) #Chocolate brown color
            qp.setPen(pen)
            
            #Draw contour lines
            for c in self.__contours:
                qp.drawLine(c.getStart(), c.getEnd())
            
        #Set properties, points
        pen.setWidth(15)
        pen.setColor(Qt.GlobalColor.black)
        qp.setPen(pen)
   
        #Draw points
        qp.drawPoints(self.__points)
        
        #End draw
        qp.end()
    
        
    def getDT(self):
        return self.__DT
    
        
    def setDT(self, DT):
        #Set DT
        self.__DT = DT
        
        
    def getPoints(self):
        #Get points
        return self.__points
    
    
    def clearResult(self):
        #Clear results of analyses
        self.__DT.clear()
           
        #Repaint screen
        self.repaint()
        
        
    def setContours(self, contours):
        #Set contour lines
        self.__contours = contours
    
    
    def getTriangles(self):
        #Get triangles
        return self.__triangles
    

    def setTriangles(self, triangles):
        #Set triangles
        self.__triangles = triangles
    
    
    def setViewDT(self, view):
        #Set view DT
        self.__view_DT = view
        

    def setViewSlope(self, view):
        #Set view Slope
        self.__view_Slope = view
        

    def setViewAspect(self, view):
        #Set view Aspect
        self.__view_Aspect = view
        
        
    def setViewContours(self, view):
        #Set view contours
        self.__view_Contours = view
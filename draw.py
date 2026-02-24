from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = QPolygonF()
        self.__q = QPointF(-100, -100)
        self.__add_vertex = False
       
        
    def mousePressEvent(self, e):
        #Get position
        x = e.position().x()
        y = e.position().y()
        
        #Add new vertex to polygon
        if self.__add_vertex:
            #Create new point
            p = QPointF(x,y)
            
            #Add point to polygon
            self.__pol.append(p)
            
        #Change q position
        else:
            self.__q.setX(x)
            self.__q.setY(y)
            
        #Repaint screen
        self.repaint()


    def paintEvent(self, e):
        #Repaint screen
        
        #New object
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #Graphic attributes, polygon
        qp.setPen(Qt.GlobalColor.red)
        qp.setBrush(Qt.GlobalColor.yellow)
        
        #Draw polygon
        qp.drawPolygon(self.__pol)
        
        #Graphic attributes, point
        qp.setPen(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.white)
        
        #Point radius
        r = 5
        qp.drawEllipse(int(self.__q.x() -r), int(self.__q.y() - r), 2*r, 2*r )
        
        #End draw
        qp.end()
        
        
    def changeStatus(self):
        #Change status: draw point / polygon
        self.__add_vertex = not(self.__add_vertex)

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from algorithms import Algorithms
from polygon import Polygon

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = [Polygon()]    #An array of all polygons on screen with their id
        self.__q = QPointF(-100, -100)
        self.__add_vertex = True
        self.__algo = Algorithms()
       
        
    def mousePressEvent(self, e):
        #Get position
        x = e.position().x()
        y = e.position().y()
        
        #Add new vertex to polygon
        if self.__add_vertex:
            #Create new point
            p = QPointF(x,y)
            
            #Add point to polygon
            self.__pol[0].addVertex(p)
            
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
        
        #Draw all polygons
        for poly in self.__pol:
            qp.drawPolygon(poly)
        
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
        
        
    def clearSelection(self):
        #Clears entire canvas
        self.__q = QPointF(-100, -100)
        self.__pol[0].clear()
        
        #Repaints cleared screen
        self.repaint()
    
    def showResult(self, result):
        """ Displays the result """
        #For now just prints the inside or outside
        if result:
            for poly in result:
                print(f"INSIDE {poly.id}")
            return
        
        print("OUTSIDE")
    
    def analyze(self, option):
        """ Runs the analyzation from the selected method """
        #Here we can run the preselection with min/max boxes
        polygons = self.__algo.preselectMinMax(self.__q, self.__pol)
        pol_count = len(polygons)

        result = []

        match option:
            #Ray crossing
            case 1:
                for poly in polygons:
                    #Check if the point lays in that polygon
                    if self.__algo.analyzePointAndPolygonRC(self.__q, poly):
                        #If True, append the polygon id
                        result.append(poly)
            
            #Winding number
            case 2:
                for poly in polygons:
                    #Check if the point lays in that polygon
                    if self.__algo.analyzePointAndPolygonWN(self.__q, poly):
                        #If True, append the polygon id
                        result.append(poly)
        
        self.showResult(result)
        return True

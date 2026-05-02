from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from generate_data import *
from random import *
from math import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__points = generate_points(500)
        self.__DT = []
        self.__contours = []
        self.__triangles = []
        self.__view_DT = True
        self.__view_Slope = True
        self.__view_Aspect = True
        self.__view_Contours = True
        
        self.__zoom = 1
        self.__zoom_change = 0.75
        self.__pan = [0, 0]
        self.__pan_change = 50

        #Capture key strokes
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def wheelEvent(self, event):
        #Handles mouse wheel inputs
        delta = event.angleDelta().y()

        #Stores mouse position
        mouse_pos = event.position()  # QPointF
        mx = mouse_pos.x()
        my = mouse_pos.y()

        old_zoom = self.__zoom

        #Changes zoom level
        if delta > 0:
            if self.__zoom < 1000:
                self.__zoom /= self.__zoom_change
        else:
            self.__zoom *= self.__zoom_change

        #Canvas coordinates of mouse location
        world_x = mx / old_zoom - self.__pan[0]
        world_y = my / old_zoom - self.__pan[1]

        #Pan change based on mouse location
        self.__pan[0] = mx / self.__zoom - world_x
        self.__pan[1] = my / self.__zoom - world_y

        self.__cache_dirty = True
        self.update()  # redraws surface

        event.accept()
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Up:
            self.__pan[1] += self.__pan_change / self.__zoom
        elif event.key() == Qt.Key.Key_Down:
            self.__pan[1] -= self.__pan_change / self.__zoom
        elif event.key() == Qt.Key.Key_Left:
            self.__pan[0] += self.__pan_change / self.__zoom
        elif event.key() == Qt.Key.Key_Right:
            self.__pan[0] -= self.__pan_change / self.__zoom
        self.__cache_dirty = True
        self.update()
        
    def mousePressEvent(self, e):
        #Get cursor coordinates 
        x = e.position().x() / self.__zoom - self.__pan[0]
        y = e.position().y() / self.__zoom - self.__pan[1]
        
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
        
        # Apply zoom/pan transform
        transform = QTransform()
        transform.scale(self.__zoom, self.__zoom)
        transform.translate(self.__pan[0], self.__pan[1])
        qp.setTransform(transform)

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
        qp.setPen(Qt.GlobalColor.black)   # border color
        qp.setBrush(Qt.GlobalColor.black)   # fill color
   
        #Draw points as circles that change size with zoom
        for point in self.__points:
            qp.drawEllipse(point, 3/self.__zoom, 3/self.__zoom)
        
        #End draw
        qp.end()
    
    def zoomToData(self):
        if not self.__points or len(self.__points) == 0:
            return

        #Find bounding box of all points
        x_min = float('inf')
        x_max = float('-inf')
        y_min = float('inf')
        y_max = float('-inf')

        for point in self.__points:
            x_min = min(x_min, point.x())
            x_max = max(x_max, point.x())
            y_min = min(y_min, point.y())
            y_max = max(y_max, point.y())

        data_width = x_max - x_min
        data_height = y_max - y_min

        if data_width == 0 or data_height == 0:
            return

        #Calculate zoom level to fit data in window with some padding
        padding = 0.9
        zoom_x = (self.width() * padding) / data_width
        zoom_y = (self.height() * padding) / data_height
        self.__zoom = min(zoom_x, zoom_y)

        #Center the data in the window
        self.__pan[0] = (self.width() / (2 * self.__zoom)) - (x_min + data_width / 2)
        self.__pan[1] = (self.height() / (2 * self.__zoom)) - (y_min + data_height / 2)

        self.__cache_dirty = True
        self.update()
    
    def setPointsFromLas(self, las):
        #Sets the points from a las object
        xs = las.x
        ys = las.y
        zs = las.z

        for x, y, z in zip(xs, ys, zs):
            self.__points.append(QPoint3DF(float(x), float(y), float(z)))
        
        #Zoom to the data
        self.zoomToData()

        #Update the view
        self.__cache_dirty = True
        self.update()
        
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
    
    def resetPoints(self):
        self.__points = []

    def resetDT(self):
        self.__DT = []

    def resetContours(self):
        self.__contours = []

    def resetTriangles(self):
        self.__triangles = []
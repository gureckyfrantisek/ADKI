from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__polyline = []
        #self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) #Enables key inputs
        self.__polyline_simp = []
        #self.__polyline = self.createTestPoints()
        self.__zoom = 1
        self.__zoom_change = 0.75
        self.__pan = [0, 0]
        self.__pan_change = 60
        self.__result = []
        self.__polygon_cache = QPixmap(self.size())
        self.__polygon_cache.fill(Qt.GlobalColor.transparent)
       
        
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
            #Zoom in
            if self.__zoom < 1000:
                self.__zoom /= self.__zoom_change
        else:
            #Zoom out
            self.__zoom *= self.__zoom_change

        #Canvas coordinates of mouse location
        world_x = mx / old_zoom - self.__pan[0]
        world_y = my / old_zoom - self.__pan[1]

        #Pan change based on mouse location
        self.__pan[0] = mx / self.__zoom - world_x
        self.__pan[1] = my / self.__zoom - world_y

        self.update()  # redraws surface

        event.accept()


    def mousePressEvent(self, e):
        """Handle mouse press event"""
        #Only continues with left click
        if e.button() != Qt.MouseButton.LeftButton:
            return
        
        #Widget mouse position
        x_widget = e.position().x()
        y_widget = e.position().y()

        print(x_widget, y_widget)
        
        #Transformed coordinates
        x = x_widget/self.__zoom - self.__pan[0]
        y = y_widget/self.__zoom - self.__pan[1]
        
        print(x, y)
        #Create new point
        p = QPointF(x,y)
            
        #Add point to polyline
        self.__polyline.append(p)      
      
        #Repaint screen
        self.update()


    def keyPressEvent(self, event: QKeyEvent):
        #Handles key inputs
        
        #Section for moving the canvas (PAN)
        if event.key() == Qt.Key.Key_Up:
            self.__pan[1] += self.__pan_change / self.__zoom

        elif event.key() == Qt.Key.Key_Down:
            self.__pan[1] -= self.__pan_change / self.__zoom

        elif event.key() == Qt.Key.Key_Left:
            self.__pan[0] += self.__pan_change / self.__zoom

        elif event.key() == Qt.Key.Key_Right:
            self.__pan[0] -= self.__pan_change / self.__zoom

        self.update()
        

    def paintEvent(self, event):
        qp = QPainter(self)

        #Set transform parameters
        transform = QTransform()
        transform.scale(self.__zoom, self.__zoom) 
        transform.translate(self.__pan[0], self.__pan[1])

        qp.setPen(Qt.GlobalColor.black)

        if self.__polyline:
            #Draw polyline
            poly = QPolygonF(self.__polyline)
            qp.drawPolyline(transform.map(poly))
            #Graphic attributes, simplified polyline
            
            #Draw simplified polyline
            qp.setPen(Qt.GlobalColor.red)
            poly_simp = QPolygonF(self.__polyline_simp)
            qp.drawPolyline(transform.map(poly_simp))
            
        qp.end()
        
        
    def clearCanvas(self):
        #Clears the canvas
        self.__polyline.clear()
        self.__polyline_simp.clear()

        self.repaint()


    def clearResult(self):
        #Clear results of analyses
        self.__polyline_simp.clear()
           
        #Repaint screen
        self.repaint()

    
    def getPolyline(self):
        #Get polyline
        return self.__polyline
    

    def setPolylineSimp(self, polyline_simp):
        #Set simplified polyline
        self.__polyline_simp = polyline_simp

    
    def getPolylineSimp(self):
        #Set simplified polyline
        return self.__polyline_simp
    

    def createTestPoints(self):

        points = []
        xy_coor = [(0, 0), (0, 1), (1, 0), (2, -1), (2, 0)]

        for p in xy_coor:
            points.append(QPointF(200 + p[0]*100, 200 + p[1]*100))

        return QPolygonF(points)
     

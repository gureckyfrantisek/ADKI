from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import shapefile as shp

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__polylines = [[]]
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) #Enables key inputs
        self.__polylines_simp = []
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
        self.__polylines[-1].append(p)
      
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

        #Draw polylines
        qp.setPen(Qt.GlobalColor.black)
        for pl in self.__polylines:
            if len(pl) >= 2:
                qp.drawPolyline(transform.map(QPolygonF(pl)))

        #Draw simplified polylines
        qp.setPen(Qt.GlobalColor.red)
        for pl in self.__polylines_simp:
            if len(pl) >= 2:
                qp.drawPolyline(transform.map(QPolygonF(pl)))

        qp.end()
        
        
    def clearCanvas(self):
        #Clears the canvas
        self.__polylines = [[]]
        self.__polylines_simp = []

        self.repaint()


    def clearResult(self):
        #Clear results of analyses
        self.__polylines_simp = []

        #Repaint screen
        self.repaint()

    
    def getPolylines(self):
        #Get polylines
        return [pl for pl in self.__polylines if len(pl) >= 2]


    def setPolylinesSimp(self, polylines_simp):
        #Set simplified polylines
        self.__polylines_simp = polylines_simp


    def getPolylinesSimp(self):
        #Get simplified polylines
        return self.__polylines_simp
    

    def createTestPoints(self):

        points = []
        xy_coor = [(0, 0), (0, 1), (1, 0), (2, -1), (2, 0)]

        for p in xy_coor:
            points.append(QPointF(200 + p[0]*100, 200 + p[1]*100))

        return QPolygonF(points)


    def saveSHPData(self, sf):
        self.__polylines = []
        for shape in sf.shapes():
            part_ends = list(shape.parts[1:]) + [len(shape.points)]
            for start, end in zip(shape.parts, part_ends):
                pts = [QPointF(x, -y) for x, y in shape.points[start:end]]
                if len(pts) >= 2:
                    self.__polylines.append(pts)


    def getFile(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Shapefiles (*.shp);;All Files (*)")
        return file


    def handleFileOpen(self):
        file = self.getFile()
        if not file:
            return
        sf = shp.Reader(file)
        self.saveSHPData(sf)
        self.__polylines_simp = []
        self.zoomToData()


    def zoomToData(self):
        all_pts = [p for pl in self.__polylines for p in pl]
        if not all_pts or self.width() == 0 or self.height() == 0:
            return

        x_min = min(p.x() for p in all_pts)
        x_max = max(p.x() for p in all_pts)
        y_min = min(p.y() for p in all_pts)
        y_max = max(p.y() for p in all_pts)

        w = x_max - x_min
        h = y_max - y_min
        if w == 0 or h == 0:
            return

        padding = 0.9
        self.__zoom = min((self.width() * padding) / w, (self.height() * padding) / h)
        self.__pan[0] = (self.width() / (2 * self.__zoom)) - (x_min + w / 2)
        self.__pan[1] = (self.height() / (2 * self.__zoom)) - (y_min + h / 2)
        self.update()


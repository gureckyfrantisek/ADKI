from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from polygon import Polygon
import shapefile as shp
import datetime

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) #Enables key inputs
        self.__pol = [Polygon()]    #An array of all polygons on screen with their id
        self.__zoom = 1
        self.__zoom_change = 0.75
        self.__pan = [0, 0]
        self.__pan_change = 60
        self.__result = []
        self.__polygon_cache = QPixmap(self.size())
        self.__polygon_cache.fill(Qt.GlobalColor.transparent)
        self.__cache_dirty = True


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

        self.__cache_dirty = True
        self.update()  # redraws surface

        event.accept()
        
        
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

        self.__cache_dirty = True
        self.update()
        
        
    def mousePressEvent(self, e):
        #Get position
        
        #Only continues with left click
        if e.button() != Qt.MouseButton.LeftButton:
            return

        #Widget mouse position
        x_widget = e.position().x()
        y_widget = e.position().y()
        
        #Transformed coordinates
        x = x_widget/self.__zoom - self.__pan[0]
        y = y_widget/self.__zoom - self.__pan[1]
        
        #Create new point
        p = QPointF(x,y)
        
        #Add point to polygon
        self.__pol[0].addVertex(p)
            
        #Repaint screen
        self.__cache_dirty = True
        self.update()


    def recalculateFeatures(self, zoom_change):
        # Momentálně se nepoužívá, mění přímo souřadnice bodů, což asi nechceme
        new_polygons = []
        for pol in self.__pol:
            scaled = Polygon()
            for point in pol:
                scaled.append(QPointF(point.x()*zoom_change, point.y()*zoom_change))
            new_polygons.append(scaled)
        
        self.__pol = new_polygons


    def paintEvent(self, e):
        """ Repaints the screen """
        if self.__cache_dirty:
            
            #Creates polygon cache
            self.__polygon_cache = QPixmap(self.size())
            self.__polygon_cache.fill(Qt.GlobalColor.transparent)

            #New cache painter
            cache_painter = QPainter(self.__polygon_cache)
            
            #Transform definition for polygons
            transform = QTransform()
            transform.scale(self.__zoom, self.__zoom)
            transform.translate(self.__pan[0], self.__pan[1])
            
            #Draw all polygons
            cache_painter.setPen(Qt.GlobalColor.red)
            cache_painter.setBrush(Qt.GlobalColor.yellow)
            for poly in self.__pol:
                cache_painter.drawPolygon(transform.map(poly))
            
            #Draw result polygons
            cache_painter.setPen(Qt.GlobalColor.blue)
            cache_painter.setBrush(Qt.GlobalColor.cyan)
            cache_painter.setOpacity(0.4)
            for poly in self.__result:
                cache_painter.drawPolygon(transform.map(poly))
            
            #End draw
            cache_painter.end()
            
            self.__cache_dirty = False
            
        #Paint cached image to canvas
        qp = QPainter(self)
        qp.drawPixmap(0, 0, self.__polygon_cache)

    
    def printResult(self, log):
        """ Displays the result """
        #For now just prints the inside or outside
        if self.__result:
            for poly in self.__result:
                log.appendPlainText(f"    INSIDE {poly.id}")
            return
        
        log.appendPlainText(f"    OUTSIDE")

    
    def getTimeStr(self):
        now = datetime.datetime.now()
        time = str(now.time())
        return f"[{time}] "
    
    def bboxToQPoint(self, bbox, offset):
        """Transfers the shp format to an array of two QPointF's"""
        x_min = bbox[0] + offset[0]
        x_max = bbox[2] + offset[0]
        y_min = -bbox[3] - offset[1]
        y_max = -bbox[1] - offset[1]

        #By inverting the y axis the min and max also invert on screen

        return [QPointF(x_min, y_min), QPointF(x_max, y_max)]

    def saveSHPData(self, sf, log):
        self.__pol = []  #Clear existing polygons
        offset = (675000, 1100000)

        for i, shape in enumerate(sf.shapes()):
            poly = Polygon()
            poly.id = i
            poly.bbox = self.bboxToQPoint(shape.bbox, offset)

            for x, y in shape.points:
                #X is right and Y is down on screen
                #The coordinates in shape are inverted and interchanged
                poly.addVertex(QPointF(x + offset[0], -y - offset[1]))

            self.__pol.append(poly)
        
        log.appendPlainText(f"{self.getTimeStr()}Loaded {len(self.__pol)} polygon(s) from file.")
    
    def getFile(self, log):
        log.appendPlainText(f"{self.getTimeStr()}Opening file dialog.")

        file, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Shapefiles (*.shp);;All Files (*)")
        
        log.appendPlainText(f"{self.getTimeStr()}File open: {file}.")

        return file
    
    def handleFileOpen(self, log):
        #First we get the file
        file = self.getFile(log)

        #If no file was selected, return
        if (not file):
            return
        
        #Then we read it
        sf = shp.Reader(file)

        #Save the polygons to our data structure
        self.saveSHPData(sf, log)

        #If it's the showcase data, change the pan and zoom to Czechia
        if file.find("/data/"):
            self.__pan = [350000, 200000]
            self.__zoom = 0.0012

        #Display the new polygons
        self.__cache_dirty = True
        self.update()
    
    
    def getPolygon(self):
        #Get polygon 
        return self.__pol
    

    def appendPolygon(self, pol):
        #Appends polygon to private list
        new_pol = Polygon(id=1)
        new_pol.addQPolygonF(pol)
        self.__pol.append(new_pol)
        
    def appendResult(self, pol):
        #Appends polygon to private result list
        new_pol = Polygon(id=1)
        new_pol.addQPolygonF(pol)
        self.__result.append(new_pol)
        
    def clearResult(self):
        """ Clears the result """
        self.__result = []
        
        #Repaints cleared screen
        self.__cache_dirty = True
        self.update()

    def clearSelection(self, log):
        """ Clears entire canvas """
        self.__pol = [Polygon()]
        self.__result = []
        self.__cache_dirty = True
        #Repaints cleared screen
        self.update()
        log.appendPlainText(f"{self.getTimeStr()}Canvas cleared.")
        
    def trueCacheDirty(self):
        self.__cache_dirty = not(self.__cache_dirty)
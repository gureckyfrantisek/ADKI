from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from algorithms import Algorithms
from polygon import Polygon
import shapefile as shp
import datetime

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) #Enables key inputs
        self.__pol = [Polygon()]    #An array of all polygons on screen with their id
        self.__q = QPointF(-100, -100)
        self.__add_vertex = True
        self.__algo = Algorithms()
        self.__zoom = 1
        self.__zoom_change = 0.9
        self.__pan = [0, 0]
        self.__pan_change = 40
        self.__result = []
       
    def wheelEvent(self, event):
        #Handles mouse wheel inputs
        delta = event.angleDelta().y()

        if delta > 0:
            #Zoom in
            if self.__zoom < 1000:
                self.__zoom /= self.__zoom_change
        else:
            #Zoom out
            self.__zoom *= self.__zoom_change
            
        print(self.__zoom)
        self.repaint()
        event.accept()  #Mark event as handled
        
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

        print(self.__pan)
        self.repaint()
        
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

    def recalculateFeatures(self, zoom_change):
        # Momentálně se nepoužívá, mění přímo souřadnice bodů, což asi nechceme
        self.__q = QPointF(self.__q.x()*zoom_change, self.__q.y()*zoom_change)
        
        new_polygons = []
        for pol in self.__pol:
            scaled = Polygon()
            for point in pol:
                scaled.append(QPointF(point.x()*zoom_change, point.y()*zoom_change))
            new_polygons.append(scaled)
        
        self.__pol = new_polygons

    def paintEvent(self, e):
        #Repaint screen
        
        #New object
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #Graphic attributes, polygon
        qp.setPen(Qt.GlobalColor.red)
        qp.setBrush(Qt.GlobalColor.yellow)
        
        #Transform definition for polygons
        transform = QTransform()
        transform.scale(self.__zoom, self.__zoom)
        transform.translate(self.__pan[0], self.__pan[1])
        
        #Draw all polygons
        for poly in self.__pol:
            #If it's the result poly, color it red
            if poly in self.__result:
                qp.setPen(Qt.GlobalColor.yellow)
                qp.setBrush(Qt.GlobalColor.red)
            
                qp.drawPolygon(transform.map(poly))
                
                qp.setPen(Qt.GlobalColor.red)
                qp.setBrush(Qt.GlobalColor.yellow)

            else:
                qp.drawPolygon(transform.map(poly))
                
        #Graphic attributes, point
        qp.setPen(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.white)
        
        #Point radius
        r = 5
        transformed_x = (self.__q.x() + self.__pan[0])*self.__zoom
        transformed_y = (self.__q.y() + self.__pan[1])*self.__zoom
        qp.drawEllipse(int(transformed_x - r) , int(transformed_y - r) , 2*r, 2*r )
        
        #End draw
        qp.end()
        
        
    def changeStatus(self, log):
        """ Changes status: draw point / polygon """
        self.__add_vertex = not(self.__add_vertex)
        
        if self.__add_vertex:
            log.appendPlainText(f"{self.get_time_str()}Polygon selected.")
        else:
            log.appendPlainText(f"{self.get_time_str()}Point selected.")
        
        
    def clearSelection(self, log):
        """ Clears entire canvas """
        self.__q = QPointF(-100, -100)
        self.__pol = [Polygon()]
        
        #Repaints cleared screen
        self.repaint()
        log.appendPlainText(f"{self.get_time_str()}Canvas cleared.")
    
    def printResult(self, log):
        """ Displays the result """
        #For now just prints the inside or outside
        if self.__result:
            for poly in self.__result:
                log.appendPlainText(f"    INSIDE {poly.id}")
            return
        
        log.appendPlainText(f"    OUTSIDE")

    
    def analyze(self, option, log):
        """ Runs the analyzation from the selected method """
        #Here we can run the preselection with min/max boxes
        polygons = self.__algo.preselectMinMax(self.__q, self.__pol)
        pol_count = len(polygons)
    
        #Reset the result
        self.__result = []

        match option:
            #Ray crossing
            case 1:
                log.appendPlainText(f"{self.get_time_str()}Analyze point (Ray crossing).")
                for poly in polygons:
                    #Check if the point lays in that polygon
                    if self.__algo.analyzePointAndPolygonRC(self.__q, poly):
                        #If True, append the polygon id
                        self.__result.append(poly)
            
            #Winding number
            case 2:
                log.appendPlainText(f"{self.get_time_str()}Analyze point (Winding number).")
                for poly in polygons:
                    #Check if the point lays in that polygon
                    if self.__algo.analyzePointAndPolygonWN(self.__q, poly):
                        #If True, append the polygon id
                        self.__result.append(poly)
        
        self.printResult(log)
        self.repaint()
        return True
    
    def get_time_str(self):
        now = datetime.datetime.now()
        time = str(now.time()).split(".")[0]
        return f"[{time}] "
    
    def bboxToQPoint(self, bbox):
        """Transfers the shp format to an array of two QPointF's"""
        return [QPointF(bbox[0], bbox[1]), QPointF(bbox[2], bbox[3])]

    def saveSHPData(self, sf, log):
        self.__pol = []  #Clear existing polygons
        
        for i, shape in enumerate(sf.shapes()):
            poly = Polygon()
            poly.id = i
            poly.bbox = self.bboxToQPoint(shape.bbox)

            for x, y in shape.points:
                #X is right and Y is down on screen
                #The coordinates in shape are inverted and interchanged
                offset = (675000, 1100000)

                poly.addVertex(QPointF(x + offset[0], -y - offset[1]))

            self.__pol.append(poly)
        
        log.appendPlainText(f"{self.get_time_str()}Loaded {len(self.__pol)} polygon(s) from file.")
    
    def getFile(self, log):
        log.appendPlainText(f"{self.get_time_str()}Opening file dialog.")

        file, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Shapefiles (*.shp);;All Files (*)")
        
        log.appendPlainText(f"{self.get_time_str()}File open: {file}.")

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

        #Change input mode to point
        self.__add_vertex = False

        #Display the new polygons
        self.repaint()
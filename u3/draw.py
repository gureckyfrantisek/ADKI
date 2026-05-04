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

        self.__rotating = False
        self.__rot_x = 0
        self.__rot_y = 0
        self.__last_mouse_pos = None

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
            factor = 1 / self.__zoom_change
        else:
            factor = self.__zoom_change

        new_zoom = self.__zoom * factor

        #Clamp zoom
        new_zoom = max(0.1, min(100, new_zoom))

        #Point in screen-space relative to center + pan
        cx = self.width() / 2 + self.__pan[0]
        cy = self.height() / 2 + self.__pan[1]

        #Vector from center to cursor
        vx = mx - cx
        vy = my - cy

        #Scale that vector
        scale = new_zoom / old_zoom

        #Adjust pan so cursor stays fixed
        self.__pan[0] = self.__pan[0] - vx * (scale - 1)
        self.__pan[1] = self.__pan[1] - vy * (scale - 1)

        #Apply zoom
        self.__zoom = new_zoom

        #Update view
        self.update()
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
        elif event.key() == Qt.Key.Key_R:
            self.__rot_x = 0
            self.__rot_y = 0
        self.__cache_dirty = True
        self.update()
        
    def mousePressEvent(self, e):
        #If where holding Ctrl, do not add points but rotate
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.__rotating = True
            self.__last_mouse_pos = e.position()
            return
        
        #Screen coords
        mx = e.position().x()
        my = e.position().y()

        #Undo pan + zoom + screen center
        x = (mx - self.width()/2 - self.__pan[0]) / self.__zoom
        y = (my - self.height()/2 - self.__pan[1]) / self.__zoom

        #Approximate inverse projection
        #Undo projection offset
        _, _, cz = self.get_center()
        z = cz

        #Undo rotation (inverse rotation = -angles)
        x, y, z = self.rotate_point(x, y, z, -self.__rot_x, -self.__rot_y)

        #Undo centering
        cx, cy, cz = self.get_center()
        x += cx
        y += cy

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
        
    def mouseReleaseEvent(self, e):
        #Not holding down anymore, stop rotating
        self.__rotating = False
        self.__last_mouse_pos = None
    
    def mouseMoveEvent(self, e):
        if not self.__rotating or self.__last_mouse_pos is None:
            return

        #Calculate differences
        dx = e.position().x() - self.__last_mouse_pos.x()
        dy = e.position().y() - self.__last_mouse_pos.y()

        #Add to rotation slowly
        self.__rot_y += dx * 0.003
        self.__rot_x += dy * 0.003
        
        #Keep the DT facing upwards
        limit = pi - 0.1
        self.__rot_x = max(-limit, min(-0.1, self.__rot_x))

        #Update last mouse position
        self.__last_mouse_pos = e.position()
        self.update()
    
    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Create new pen
        pen = QPen()
        
        # Apply zoom/pan transform
        transform = QTransform()
        transform.scale(self.__zoom, self.__zoom)
        transform.translate(self.__pan[0], self.__pan[1])
        qp.setTransform(transform)

        #Draw slope or aspect, not both
        if self.__view_Slope or self.__view_Aspect:
            pen.setColor(Qt.GlobalColor.black)
            qp.setPen(pen)

            #Process all triangles
            triangles = sorted(self.__triangles, key=self.depth, reverse=True)

            for triangle in triangles:
                if self.__view_Slope:
                    #Get slope
                    slope = triangle.getSlope()

                    #Rescale slope to 0-255
                    k = (2 * 255) / pi
                    gray = max(0, min(255, int(255 - (slope * k))))

                    #Create Qt Color
                    color = QColor(gray, gray, gray)
                else:
                    #Get aspect
                    aspect = triangle.getAspect()

                    #Rescale aspect to 0-1
                    aspect_normed = aspect / (2 * pi)
                    
                    #Create Qt Color
                    color = QColor.fromHsvF(aspect_normed, 1, 1)

                #Assign brush color
                qp.setBrush(color)

                #Draw transformed polygon
                p1 = self.transform_point(triangle.getP1())
                p2 = self.transform_point(triangle.getP2())
                p3 = self.transform_point(triangle.getP3())

                pol = QPolygonF([p1, p2, p3])
                
                qp.drawPolygon(pol)
            
        #Draw DT
        if self.__view_DT:
            #Set properties, edges
            pen.setColor(Qt.GlobalColor.green)
            qp.setPen(pen)
            
            #Draw edges
            for e in self.__DT:
                p1 = self.transform_point(e.getStart())
                p2 = self.transform_point(e.getEnd())
                qp.drawLine(p1, p2)

        #Draw contour lines
        if self.__view_Contours:        
            #Set properties, contours
            pen.setColor(QColor(85, 38, 0)) #Chocolate brown color
            qp.setPen(pen)
            
            #Draw contour lines
            for c in self.__contours:
                p1 = self.transform_point(c.getStart())
                p2 = self.transform_point(c.getEnd())
                qp.drawLine(p1, p2)
            
        #Set properties, points
        pen.setWidth(15)
        pen.setColor(Qt.GlobalColor.black)
        qp.setPen(Qt.GlobalColor.black)   # border color
        qp.setBrush(Qt.GlobalColor.black)   # fill color
   
        #Draw points as circles that change size with zoom
        for point in self.__points:
            p = self.transform_point(point)
            qp.drawEllipse(p, 3, 3)
        
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
    
    def rotate_point(self, x, y, z, ax, ay):
        #Rotation around X
        y2 = y * cos(ax) - z * sin(ax)
        z2 = y * sin(ax) + z * cos(ax)

        #Rotation around Y
        x3 = x * cos(ay) + z2 * sin(ay)
        z3 = -x * sin(ay) + z2 * cos(ay)

        #Return rotated point
        return x3, y2, z3

    def project_point(self, x, y, z, d=1000):
        z += 2000
        factor = d / z
        return x * factor, y * factor

    def transform_point(self, p):
        x, y, z = p.x(), p.y(), p.z()

        #Centering
        cx, cy, cz = self.get_center()
        x -= cx
        y -= cy
        z -= cz

        #Rotation
        x, y, z = self.rotate_point(x, y, z, self.__rot_x, self.__rot_y)

        #Projection of the point
        x, y = self.project_point(x, y, z)

        #Adjust with pan and zoom
        x = x * self.__zoom + self.width() / 2 + self.__pan[0]
        y = y * self.__zoom + self.height() / 2 + self.__pan[1]

        return QPointF(x, y)
    
    def depth(self, tri):
        #Calculates the triangle depth for drawing
        z1 = self.rotate_point(tri.getP1().x(), tri.getP1().y(), tri.getP1().z(), self.__rot_x, self.__rot_y)[2]
        z2 = self.rotate_point(tri.getP2().x(), tri.getP2().y(), tri.getP2().z(), self.__rot_x, self.__rot_y)[2]
        z3 = self.rotate_point(tri.getP3().x(), tri.getP3().y(), tri.getP3().z(), self.__rot_x, self.__rot_y)[2]

        return (z1 + z2 + z3) / 3

    def get_center(self):
        if not self.__points:
            return 0, 0, 0

        #Initialize sums
        n = len(self.__points)
        x_sum, y_sum, z_sum = 0, 0, 0

        #Sum the coordinates
        for point in self.__points:
            x_sum += point.x()
            y_sum += point.y()
            z_sum += point.z()

        #Return averages
        return x_sum/n, y_sum/n, z_sum/n

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
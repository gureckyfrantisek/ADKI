from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *
from collections import deque
import sys

class Algorithms:
    
    def __init__(self):
        pass
    
    def get2LinesAngle(self, p1, p2, p3, p4):
        #Calculates the angle between two lines
        
        #Vector u
        ux = p2.x() - p1.x()
        uy = p2.y() - p1.y()
        
        #Vector v
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()
        
        #Dot product
        dot = ux * vx + uy * vy
                
        #Norms
        norm_u = sqrt(ux**2 + uy**2)
        norm_v = sqrt(vx**2 + vy**2)
        
        #Compute phi
        phi = acos(dot / (norm_u * norm_v))
        
        return phi
    
    
    def get2PointDistance(self, p1, p2):
        #x, y distance
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        # distance
        distance = sqrt(dx**2 + dy**2)
        return distance
    
    
    def createCH(self, pol: QPolygonF):
        """Creates Convex Hull of inserted polygon"""
        # Graham Scan (can add more methods later)
        print("začátek CH")

        # ensure polygon is creatable
        if len(pol) <= 2:
            return False
        
        # pivot is the point with the most bottom coordinate (max Y)
        max_y = pol[0].y()
        pivot = pol[0]
        min_x = pol[0].x()
        # finds pivot
        for point in pol:

            # checks if point's y is > than current max
            if point.y() > max_y:
                max_y = point.y()
                pivot = point
            # checks if point's x is < than current min
            if point.x() < min_x:
                min_x = point.x()

        angle_pivot = QPointF(min_x, max_y)
        
        # calculates angles and distances to create starshape
        pointDistAngle = [] #this list has list for each point, in inner list is the point, distance from pivot to point and angle
        
        for point in pol:
            # ensure point is not the pivot
            if pivot == point:
                continue
            # now it does not care about distance 
            pointDistAngle.append([point, self.get2PointDistance(pivot, point), self.get2LinesAngle(angle_pivot, pivot, pivot, point)])
            
        # starshape creation
        pointDistAngle.sort(key=lambda x: x[2], reverse=True)

        starShape = QPolygonF()
        starShape.append(pivot)

        for pointList in pointDistAngle:
            starShape.append(pointList[0])
            
        #Graham cycle
        # imports stack from collections module
        stack = deque() 
        j = 2
        n = len(starShape)
        stack.append(starShape[0]) # pivot
        stack.append(starShape[1]) # p1
        
        while j < n:
            top = stack.pop()
            
            # while turn is not left
            while len(stack) > 0 and self.analyzePointAndLineRelation(stack[-1], top, starShape[j]) <= 0:
                top = stack.pop()

            stack.append(top)
            stack.append(starShape[j])

            j += 1
            
        convexHull = QPolygonF()
        while stack:
            convexHull.append(stack.pop())
            
        return convexHull

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import sys
import math

class Algorithms:
    
    def __init__(self):
        pass
    
    def analyzePointAndPolygonRC(self, q, pol):
        """ Analyze point and polygon position using Ray Crossing Algorithm """
        k = 0            # number of intrescts
        n = len(pol)     # polygon vertices count
        
        # Process all points
        for i in range(n):
            #Calculate x and y differences
            xi_red = pol[i].x() - q.x()
            yi_red = pol[i].y() - q.y()
            
            xii_red = pol[(i+1) % n].x() - q.x()
            yii_red = pol[(i+1) % n].y() - q.y()
            
            #Appropriate segment
            if ((yii_red > 0) and (yi_red <= 0)) or ((yi_red > 0) and (yii_red <= 0)):
                # Compute segment and ray intersection
                x_m = (xii_red * yi_red - xi_red * yii_red) / (yii_red - yi_red)
                
                #Increment amount of intersections
                if x_m > 0:
                    k=k+1
        
        #Point q inside pol
        if (k % 2 == 1):
            return True
        
        #Point q outside pol
        return False
    
    def calculateAngle(self, a, b, c):
        """ Calculates the angle (A, B, C) """
        #Vectors from b to a, and b to c
        ux = a.x() - b.x()
        uy = a.y() - b.y()
        vx = c.x() - b.x()
        vy = c.y() - b.y()

        #Vector lengths
        d_u = math.sqrt(ux**2 + uy**2)
        d_v = math.sqrt(vx**2 + vy**2)

        #If q lies on a vertex, return 0
        if d_u == 0 or d_v == 0:
            return 0.0

        #Clamp the cos value to avoid error from float imprecision
        cos_theta = max(-1.0, min(1.0, (ux * vx + uy * vy) / (d_u * d_v)))

        return math.acos(cos_theta)

    def analyzePointAndLineRelation(self, q, a, b):
        """ Analyze the point and oriented line relation """
        # Calculate the cross product
        cross = (b.x() - a.x()) * (q.y() - a.y()) - (b.y() - a.y()) * (q.x() - a.x())

        tolerance = sys.float_info.epsilon * 10

        if cross > tolerance:  return  1   # left  / above
        if cross < -tolerance: return -1   # right / below
        return 0                                        # on the line

    def analyzePointAndPolygonWN(self, q, pol):
        """ Analyze point and polygon position using Winding Number Algorithm """
        #Initialize
        Omega = 0           #Sum of angles
        tolerance = sys.float_info.epsilon * 10
        n = len(pol)        #Number of polygon points

        #For all points
        for i in range(n):
            p_i = pol[i]
            p_ii = pol[(i+1) % n]

            #Determine position
            position = self.analyzePointAndLineRelation(q, p_i, p_ii)

            #If we're on the line, return True for being inside
            #This takes care of the singular cases aswell
            if position == 0:
                return True
            
            #Calculate angle (p_i, q, p_ii)
            angle = self.calculateAngle(p_i, q, p_ii)
            
            #Add to the Omega sum signed by the position
            Omega = position * angle

        #Check if Omega is equal to 2pi with float precission
        if abs(abs(Omega) - 2 * math.pi) < tolerance:
            #Point q inside pol
            return 1
        
        #Point q outside pol
        return 0

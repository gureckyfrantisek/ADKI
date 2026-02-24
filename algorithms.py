from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

class Algorithms:
    
    def __init__(self):
        pass
    
    def analyzePointAndPolygonRC(self,q,pol):
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
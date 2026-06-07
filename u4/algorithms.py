from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *

class Algorithms():   
     
    def getPolygonArea(self, pol: QPolygonF):
        #Calculate polygon area  using LH formula
        #Return signed area
        area = 0
        n = len(pol)

        #Process all edges
        for i in range(n):
            area += pol[i].x() * (pol[(i+1)%n].y() - pol[(i-1+n)%n].y())
        
        return area/2


    def getPointLineDistance(self, p: QPointF, p1: QPointF, p2: QPointF):
        #Distance of the point from the line
        numerator = p.x()*(p1.y()-p2.y()) + p1.x()*(p2.y()-p.y()) + p2.x()*(p.y()-p1.y())
        denominator = sqrt((p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)

        return abs(numerator/denominator)


    def dp(self, pol, pol_simp, h, s, e):
        #Recursive Douglas-Peucker algorithm
        if (e <= s + 1):
            return
        
        #Initialize variables
        i_max = s + 1
        d_max = self.getPointLineDistance(pol[i_max], pol[s], pol[e])
        
        #Process all internal vertices
        for i in range(i_max + 1, e):
            
            #Compute distance of point from the line
            d = self.getPointLineDistance(pol[i], pol[s], pol[e])
            
            #Update maximum
            if d > d_max:
                d_max = d
                i_max = i
        
        #Furthest point outside polygon
        if d_max > h:
            
            #Process recursively the first segment
            self.dp(pol, pol_simp, h, s, i_max)
            
            #Add the furthest point
            pol_simp.append(pol[i_max])
            
            #Process recursively the second segment
            self.dp(pol, pol_simp, h, i_max, e)


    def simplifyDouglasPeucker(self, pol, h):
        #Apply Douglas Peucker algorithm
        
        #Not enough points
        if len(pol) <=2:
            return pol
        
        #Initialize 
        s = 0
        e = len(pol) - 1 
        
        #Append start point
        pol_simp = [pol[s]]

        #Recursive processing
        self.dp(pol, pol_simp, h, s, e)

        #Append end point
        pol_simp.append(pol[e])
                
        return pol_simp


    def simplifyEuclideanDistance(self, pol, d_min):
        #Simplify polyline using Euclidean distance
        #Remove points closer than d_min
        n = len(pol)

        #Not enough points
        if n <= 2:
            return pol
        
        #Always store the first point
        pol_simp = [pol[0]]
        
        #Store the last correct point
        last = pol[0]
        
        #Process all points
        for i in range(1, n):
            #Distance from the last point to the current point
            d = sqrt((last.x() - pol[i].x())**2 + (last.y() - pol[i].y())**2)
            
            #Point is too far, it becomes the last point
            if d >= d_min:
                #Add point to the list
                pol_simp.append(pol[i])
                
                #Update last point
                last = pol[i]
                
        #Store the last point
        if pol_simp[-1] != pol[-1]:
            pol_simp.append(pol[-1])
                
        return pol_simp
    
    
    def simplifyWhyatt(self, pol, area_min):
        #Simplify polyline using Whyatt algorithm
        #Initialize with the whole polyline
        pol_simp = list(pol)

        #Not enough points
        if len(pol) <= 2:
            return pol   
        
        #Initialize i
        i = 1

        while i < len(pol_simp) - 1:
            #Compute area of the triangle
            triangle_points = [pol_simp[i-1], pol_simp[i], pol_simp[i+1]]
            area = self.getPolygonArea(QPolygonF(triangle_points))

            #Check area and remove point
            if area < area_min:
                pol_simp.pop(i)
                
            #Increment index
            else:
                i = i + 1

        #Return simplified polyline
        return pol_simp
    
    
    def computeEuclideanDistance(self, p1, p2):
        #Compute euclidean distance
        dx = p1.x() - p2.x()
        dy = p1.y() - p2.y()

        return sqrt(dx**2 + dy**2)
        
            
    def computeLLR(self, pol_simp):
        #Compute local length ratio
        llr = 0
        n = len(pol_simp)

        #Not enough points, skip
        if n == 0:
            return 0
        
        for i in range(1, n-1):
            #Compute distances
            d1 = self.computeEuclideanDistance(pol_simp[i-1], pol_simp[i])
            d2 = self.computeEuclideanDistance(pol_simp[i], pol_simp[i+1])
            d3 = self.computeEuclideanDistance(pol_simp[i-1], pol_simp[i+1])

            #Compute LLR
            llr += (d1 + d2) / d3
        
        #Return mean LLR value
        return llr / (n-2)
    
    
    def findPointIndex(self, p, pol, start):
        #Find index of the point in the simplified polyline
        i = start
        
        #Repeat until p = pol[i]
        while p != pol[i]:
            i += 1
        
        #Return the found index
        return i
        
    
    def computeAreaDisplacement(self, pol_simp, pol):
        #Compute area displecement of simplified polyline
        n = len(pol_simp)
        displacement = 0
        
        #Process all segments
        for i in range(n-1):
            #Get start point index
            start = self.findPointIndex(pol_simp[i], pol, i)
            
            #Get end point index
            end = self.findPointIndex(pol_simp[i+1], pol, start+1)
            
            #Create polygon
            seg = QPolygonF(pol[start:end+1])
            area = self.getPolygonArea(seg)

            #Update displacement
            displacement += area
        
        return displacement


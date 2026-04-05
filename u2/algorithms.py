from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *
from collections import deque
import sys
import numpy as np
import numpy.linalg as npla


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
        
        #If distance between points is 0, return 0
        if norm_u == 0 or norm_v == 0:
            return 0.0

        #Clamp the cos value to avoid error from float imprecision
        cos_phi = max(-1.0, min(1.0, (dot) / (norm_u * norm_v)))

        return acos(cos_phi)
    
    
    def get2PointDistance(self, p1, p2):
        #x, y distance
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        
        # distance
        distance = sqrt(dx**2 + dy**2)
        return distance
    
    
    def analyzePointAndLineRelation(self, q, a, b):
        """ Analyze the point and oriented line relation """
        # Calculate the cross product
        cross = (b.x() - a.x()) * (q.y() - a.y()) - (b.y() - a.y()) * (q.x() - a.x())

        tolerance = sys.float_info.epsilon * 10

        if cross > tolerance:  return  1   # left  / above
        if cross < -tolerance: return -1   # right / below
        return 0    
    
    
    def createCHConvexHull(self, pol: QPolygonF):
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
            
        ###Graham cycle
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
        
        #creates QPolygonF from stack
        convexHull = QPolygonF()
        while stack:
            convexHull.append(stack.pop())
            
        return convexHull
       
    def createCHBayerVersion(self, pol:QPolygonF):
        """ Bayer version """
        #Create Convex Hull using Jarvis Scan
        ch = QPolygonF()
        
        #Find pivot q (minimize y)
        q = min(pol, key = lambda k: k.y())

        #Find left-most point (minimize x)
        s = min(pol, key = lambda k: k.x())
        
        #Initial segment
        pj = q
        pj1 = QPointF(s.x(), q.y())
        
        #Add to CH
        ch.append(pj)
        
        # Find all points of CH
        while True:
            #Maximum and its index
            omega_max = 0
            index_max = -1
            
            #Browse all points
            for i in range(len(pol)):
                
                if pj != pol[i]:
                    
                    #Compute omega
                    omega = self.get2LinesAngle(pj, pj1, pj, pol[i])
            
                    #Actualize maximum
                    if(omega>omega_max):
                        omega_max = omega
                        index_max = i
                    
            #Add point to the convex hull
            ch.append(pol[index_max])
            
            #Reasign points
            pj1 = pj
            pj = pol[index_max]
            
            # Stopping condition
            if pj == q:
                break
            
        return ch
    
    
    def createCHSweepingLine(self, pol: QPolygonF):
        """Creates Convex Hull using the sweeping line method"""
        
        # Edge case
        n = len(pol)

        if n <= 2:
            return False
        
        # Initialize
        points = list(pol)
        next = [-1] * (n)
        prev = [-1] * (n)

        # Preprocess
        points.sort(key=lambda p: (p.x(), p.y()))

        position = self.analyzePointAndLineRelation(points[2], points[0], points[1])
        if position == 0:
            return False
            
        elif position == 1:
            next[0] = 1; next[1] = 2; next[2] = 0
            prev[0] = 2; prev[1] = 0; prev[2] = 1

        else:
            next[0] = 2; next[1] = 0; next[2] = 1
            prev[0] = 1; prev[1] = 2; prev[2] = 0

        # Iterate over the rest of the points and add them continuously
        for i in range(3, n):
            if points[i].y() > points[i-1].y():
                prev[i] = i-1; next[i] = next[i-1]
            else:
                next[i] = i-1; prev[i] = prev[i-1]

            next[prev[i]] = i; prev[next[i]] = i

            while (next[next[i]] != i and
                   self.analyzePointAndLineRelation(points[next[next[i]]], points[i], points[next[i]]) == -1):
                prev[next[next[i]]] = i; next[i] = next[next[i]]
            
            while (prev[prev[i]] != i and
                   self.analyzePointAndLineRelation(points[prev[prev[i]]], points[i], points[prev[i]]) == 1):
                next[prev[prev[i]]] = i; prev[i] = prev[prev[i]]
        
        # Translate the datastructure back to a QPolygonF
        convexHull = QPolygonF()
        index = 0

        print("Starting reconstruction")
        visited = set()
        while index not in visited:
            visited.add(index)
            convexHull.append(points[index])
            index = next[index]
            # When we return, end the cycle
            if index == 0:
                return convexHull
        
        return convexHull if len(convexHull) >= 3 else False
            

    def createCH(self, pol:QPolygonF, method="convexHull"):
        """Creates Convex Hull of inserted polygon"""

        #Selects the method to create Convex Hull
        if method == "convexHull":
            return self.createCHConvexHull(pol)
        elif method == "bayer":
            return self.createCHBayerVersion(pol)
        elif method == "sweepingLine":
            return self.createCHSweepingLine(pol)


    def rotatePolygon(self, pol:QPolygonF, sig:float):
        """Rotates polygon and returns it"""
        rotated_pol = QPolygonF()
        
        for point in pol:
            # each point is transformed
            x_r = cos(sig)*point.x() - sin(sig)*point.y()
            y_r = sin(sig)*point.x() + cos(sig)*point.y()
            rotated_pol.append(QPointF(x_r, y_r)) # adds point to new rotated polygon
            
        return rotated_pol
    
    
    def createMAER(self, pol:QPolygonF):
        """Creates Minimal Area Enclosing Rectangle"""
        #input: ConvexHull QPolygonF
        minimal_rectangle = self.minMaxBox(pol) #QRectF object
        minimal_area = self.getRectArea(minimal_rectangle) 
        minimal_sig = 0
        
        n = len(pol)
        # for each edge
        for i in range(n):
            # extracts two points
            head = pol[(i+1) % n]
            tail = pol[i]
            # calculates sigma angle
            sig = atan2(head.y()-tail.y(), head.x()-tail.x())
            if sig < 0:
                sig += 2*pi
            
            # rotates the polygon and calculates it's area
            rotated_pol = self.rotatePolygon(pol, -sig)
            current_rectangle = self.minMaxBox(rotated_pol) #QRectF object
            current_area = self.getRectArea(current_rectangle) 

            # saves the parametrs if area is smaller
            if current_area < minimal_area:
                minimal_area = current_area
                minimal_rectangle = current_rectangle
                minimal_sig = sig
                
        minimal_polygon = self.QRectToQPolygon(minimal_rectangle)
        minimal_bounding_rectangle = self.rotatePolygon(minimal_polygon, minimal_sig)
        return minimal_bounding_rectangle
            
    def minMaxBox(self, pol:QPolygonF):
        # returnes minmaxbox of QPolygonF as QRectF 
        return pol.boundingRect()
        
    def QRectToQPolygon(self, rect:QRectF):
        # converts QRectF to QPolygonF
        pol = QPolygonF()
        pol.append(rect.topLeft())
        pol.append(rect.bottomLeft())
        pol.append(rect.bottomRight())
        pol.append(rect.topRight())
        return pol
    
    def getRectArea(self, rect:QRectF):
        return rect.width() * rect.height()
    
    def getPolygonArea(self, pol: QPolygonF):
        #Calculate polygon area  using LH formula
        area = 0
        n = len(pol)

        #Process all edges
        for i in range(n):
            area += pol[i].x() * (pol[(i+1)%n].y() - pol[(i-1+n)%n].y())
        
        return abs(area)/2
    
    def resizeRectangle(self, rect: QPolygonF, build: QPolygonF):
        #Resize MAER to have a similar area as a rectangle
        
        #Converts QRectF to QPolygonF if needed
        if isinstance(rect, QRectF):
            rect = self.QRectToQPolygon(rect)

        #Area of the rectangle
        rect_area = self.getPolygonArea(rect)
        
        #Area of the building
        build_area = self.getPolygonArea(build)
        
        #Area ratio
        k = (build_area / rect_area)
        
        #Compute rectangle centroid
        x_c = (rect[0].x() + rect[1].x() + rect[2].x() + rect[3].x()) / 4
        y_c = (rect[0].y() + rect[1].y() + rect[2].y() + rect[3].y()) / 4
        
        #Resized polygon
        res_rect = QPolygonF()

        for i in range(4):
            res_rect.append(QPointF((rect[i].x() - x_c)*sqrt(k) + x_c, (rect[i].y() - y_c)*sqrt(k) + y_c))
        
        return res_rect
    

    def simplifyBuildingPCA(self, building):
        #Simplify building using Principal Components Analysis
        x, y = [], []
        
        #Convert points to coordinates
        for b in building:
            x.append(b.x())
            y.append(b.y())
            
        #Create matrix
        A = np.array([x, y])
        
        #Covariance matrix
        C = np.cov(A)
        
        #Singlar value decomposition
        [U, S, V] = npla.svd(C)
        
        #Compute rotation
        sigma = atan2(V[0][1], V[0][0])
        
        #Rotate building
        building_rot = self.rotatePolygon(building, -sigma)

        #Compute min-max box 
        mmb = self.minMaxBox(building_rot)
        
        #Resize MMB
        res_mmb = self.resizeRectangle(mmb, building)
        
        #Rotate MMB
        rot_mmb = self.rotatePolygon(res_mmb, sigma)
        
        return rot_mmb


    def simplifyBuildingWallAverageAdam(self, building):
        #Simplify building using the Wall Average method    

        #number of points in the building polygon
        n = len(building)

        #Calculate sigmas for each line segment
        sigmas = []
        for point in range(n):
            #Head of the line segment
            head = building[(point+1) % n]

            #Tail of the line segment
            tail = building[point % n]

            #Sigma at the end of the line segment
            sig = atan2(head.y()-tail.y(), head.x()-tail.x())

            #Makes sure sigma is positive
            if sig < 0:
                sig += 2*pi
            sigmas.append(sig)

        #Sum of the lenghts of the line segments
        sum_s = 0
        #Sum of the remainders multiplied by the line segment lengths
        weighted_sigma_sum = 0

        for i in range(n):
            #Calculates inner angle the line segment
            omega = sigmas[i % n] - sigmas[(i - 1) % n]

            #Normalize omega to be in the range (-pi, pi)
            while omega <= -pi:
                omega += 2 * pi
            while omega > pi:
                omega -= 2 * pi

            #remainder after division
            k = round(omega / (pi / 2))
            r = omega - k * (pi / 2)

            s = self.get2PointDistance(building[i % n], building[(i + 1) % n])

            #Calculates sums for weighted average
            weighted_sigma_sum += r * s
            sum_s += s

        #Calculates rotation angle
        rot_sigma = sigmas[0] + weighted_sigma_sum/sum_s

        #Rotate building
        building_rot = self.rotatePolygon(building, -rot_sigma)

        #Compute min-max box 
        mmb = self.minMaxBox(building_rot)
        
        #Resize MMB
        res_mmb = self.resizeRectangle(mmb, building)
        
        #Rotate MMB
        rot_mmb = self.rotatePolygon(res_mmb, rot_sigma)
        
        return rot_mmb
        
    
    def simplifyBuildingLongestEdge(self, building):
        #Simplify building using longest edge method
        n = len(building)
        
        max_length = 0
        sigma = 0
        
        # Find the longest edge and its orientation
        for point in range(n):
            p1 = building[point]
            p2 = building[(point+1) % n]
            
            length = self.get2PointDistance(p1, p2)
            
            if length > max_length:
                max_length = length
                
                dx= p2.x() - p1.x()
                dy= p2.y() - p1.y()
                
                sigma = atan2(dy, dx)
        
        #Rotate building to align longest edge with x-axis
        building_rot = self.rotatePolygon(building, -sigma)
        
        #Compute axis-aligned bounding box
        mmb= self.minMaxBox(building_rot)
        
        #Resize bounding box to fit the original building
        res_mmb = self.resizeRectangle(mmb, building)
        
        #Rotate bounding box back to original orientation
        rot_mmb = self.rotatePolygon(res_mmb, sigma)
        
        return rot_mmb
                
        
    def simplifyBuildingWallAverageVitek(self,building):
        # Simplify building using wall average method
        
        n = len(building)
        sum_x = 0
        sum_y = 0
        
        # Accumulate weighted sums of wall directions
        for i in range(n):
            p1=building[i]
            p2=building[(i+1) % n]
            
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            
            length = self.get2PointDistance(p1, p2)
            
            if length == 0:
                continue
            
            sigma = atan2(dy, dx)
            
            sum_x += cos(sigma) * length
            sum_y += sin(sigma) * length
            
        # Compute average orientation
        sigma_avg = atan2(sum_y, sum_x)
        
        # Rotate building to align average direction with x-axis
        building_rot = self.rotatePolygon(building, -sigma_avg)
        
        # Compute axis-aligned bounding box
        mmb = self.minMaxBox(building_rot)
        
        # Resize bounding box to fit the original building
        res_mmb = self.resizeRectangle(mmb, building)
        
        # Rotate bounding box back to original orientation
        rot_mmb = self.rotatePolygon(res_mmb, sigma_avg)
        
        return rot_mmb
        
    
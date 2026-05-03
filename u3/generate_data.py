from random import *
from qpoint3df import *

#The script used to generate sample data
def generate_points(n):
    #Initialize the list
    points = []

    #Coordinate ranges
    x_min = 0
    x_max = 1000
    y_min = 0
    y_max = 1000
    z_min = 200
    z_max = 600
    
    #Generate points
    for _ in range(n):
        x = random() * (x_max - x_min) + x_min
        y = random() * (y_max - y_min) + y_min
        z = random() * (z_max - z_min) + z_min

        points.append(QPoint3DF(x, y, z))
    
    #Return them
    return points
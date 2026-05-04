from random import *
from qpoint3df import *

#The script used to generate sample data
def generate_points(n):
    #Initialize the list
    points = []

    #Coordinate ranges
    x_min = 0
    x_max = 800
    y_min = 0
    y_max = 600
    z_initial = 100
    z_min_rand = -10
    z_max_rand = 10
    z_flip_chance = 0.01
    neighbour_distance_tolerance = 10
    
    xy_points = []

    #Generate points
    for _ in range(n):
        x = random() * (x_max - x_min) + x_min
        y = random() * (y_max - y_min) + y_min
        xy_points.append((x, y))

    #Sort points by x and y to create a more realistic terrain
    xy_points.sort(key=lambda p: (p[0] + p[1]))

    #Generate z coordinates
    z_growing_constant = 1

    pre_xy_sum = xy_points[0][0] + xy_points[0][1]
    for x, y in xy_points:


        #Randomly flips the z growing direction to create more variation in the terrain
        if random() < z_flip_chance:
            z_growing_constant = -z_growing_constant

        #Skips close points to eliminate rapid slopes
        xy_sum = x + y
        if abs(xy_sum - pre_xy_sum) < neighbour_distance_tolerance:
            z_initial += z_growing_constant
            continue

        #Slightly increase z to create a slope
        z_initial += z_growing_constant

        #Add random variation to z
        z = z_initial + random() * (z_max_rand - z_min_rand) + z_min_rand
        points.append(QPoint3DF(x, y, z))

        #Assign new pre_xy_sum for the next iteration
        pre_xy_sum = xy_sum

    #Return them
    return points
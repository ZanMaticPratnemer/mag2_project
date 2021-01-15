from customFuncs import *
import numpy as np
import time

# TODO: remove after testing
from PyQt5.QtCore import QPoint, QPointF

class optParams(object):
    def __init__(self, r, th, f, h, a, g, next_pos, next_time):
        self.ranges = r
        self.th = th
        self.f = f
        self.h = h
        self.alpha = a
        self.gamma_max = g
        self.next_pos = next_pos
        self.next_time = next_time

def prepParameters(sel, th, f, h, alpha, gamma):
    
    ##################################
    ### Process the selected areas ###
    ##################################
    # Transform data from QPoints to numpy arrays
    areas = []
    for s in sel:
        ar = None
        for i, p in enumerate(s):
            if i == 0:
                ar = np.array([[p.x(), p.y()]], dtype=np.float32)
            else:
                ar = np.append(ar, [[p.x(), p.y()]], axis=0)
        
        areas.append(np.transpose(ar))

    # Rotate for -th around (0,0)
    rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
    rot_areas = []
    for i, area in enumerate(areas):
        rot_areas.append(rot @ area)
    # Path of flight is aligned with y axis and we only have to optimize number of flights used and their angle of recording

    # From these areas we only need x values of points because we are now looking for vertical strips which are only bound by x coordinates
    x_areas = []
    for area in rot_areas:
        x_areas.append(area[0,:])

    # Find the outermost x coordinates of all selections and store them in "ranges"
    ranges = findOuter(x_areas)

    # Check if any ranges overlap
    combine = []
    for i, range1 in enumerate(ranges):
        for j, range2 in enumerate(ranges):
            if i >= j:
                continue

            if (range1[0] < range2[1] and range1[0] > range2[0]) or (range1[1] < range2[1] and range1[1] > range2[0]):
                new_group = True
                for group in combine:
                    if (i in group) or (j in group):
                        group.add(i)
                        group.add(j)
                        new_group = False
                if new_group:
                    combine.append({i, j})
    
    # And combine those overlaping ranges
    c_ranges = []
    for group in combine:
        cluster = np.array([])
        for e in group:
            cluster = np.append(cluster, ranges[e])
        c_ranges.append(cluster)

    # Add the non everlaping ranges to the new range list
    for i in range(len(ranges)):
        add = True
        for group in combine:
            if i in group:
                add = False
                break

        if add:
            c_ranges.append(ranges[i])

    # Again find the outermost x coords
    ranges = findOuter(c_ranges)

    ######################################
    ### Get the next available passing ###
    ######################################
    start_str = "3. 9. 2020, 8:00"
    start_time = time.mktime(time.strptime(start_str, "%d. %m. %Y, %H:%M"))
    curr_time = time.time()
    # Start position in geo longitude deg
    # We presume that the satelite flew over 46.119553 latitude
    # at 14.838006 longitude
    start_pos = 14.838006

    # Orbital period in seconds
    T = 24/f * 60 * 60

    # N of deg the satelite moves each time it circles earth
    d_deg = 360/f

    time_d = curr_time-start_time
    n = np.ceil(time_d / T)

    next_pos = (d_deg * n) % 360
    next_time = start_time + T * n

    # Approximate position and time for the flight to be usefull
    while not flightValid(next_pos, next_time, ranges, th, gamma, alpha, h):
        next_time = next_time + T
        next_pos = (next_pos + d_deg) % 360

    params = optParams(ranges, th, f, h, alpha, gamma, next_pos, next_time)
    return params

def optimize(p, add_flights=0):
    T = 24/p.f * 60 * 60
    d_deg = 360/p.f
    # First check approximately with how much satelite passings we can cover all areas
    # Get the maximum picture width and divide all combined ranges with it
    # This will not always get the correct number of passings needed!!
    _, max_width = angleToWidth(p.gamma_max, p.alpha, p.h)

    print("optimize")
    
    combined_range = []
    for range in p.ranges:
        combined_range = combined_range + range[1] - range[0]
    n_of_flights = np.ceil(combined_range/max_width)*2 + add_flights


    # Get a sufficent group of flights
    flights = [[p.next_pos, p.next_time]]
    next_time = p.next_time
    next_pos = p.next_pos
    while not canCover(flights, p):
        while True:
            next_time = next_time + T
            next_pos = (next_pos + d_deg) % 360
            if flightValid(next_pos, next_time, p.ranges, p.th, p.gamma_max, p.alpha, p.h):
                break
        flights.append([next_pos, next_time])

    # Find out how many of those flights wee need and with what parameters
    print(flights)
    
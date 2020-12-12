from customFuncs import *
import numpy as np
import time

# TODO: remove after testing
from PyQt5.QtCore import QPoint, QPointF

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

    # Again find the outermost x coords
    ranges = findOuter(c_ranges)
    print(ranges)

    ######################################
    ### Get the next available passing ###
    ######################################
    start_str = "3. 9. 2020, 8:00"
    start_time = time.mktime(time.strptime(start_str, "%d. %m. %Y, %H:%M"))
    curr_time = time.time()
    # start position in geo longitude deg
    start_pos = 14.838006

    # Orbital period in seconds
    T = 24/f * 60 * 60

    # N of deg the satelite moves each time it circles earth
    d_deg = 360/f

    time_d = curr_time-start_time
    n = np.ceil(time_d / T)

    next_pos = (d_deg * n) % 360
    next_time = start_time + T * n

    

    




    



selections = [[QPoint(0, 0), QPoint(1, 0), QPoint(1, 1), QPoint(0, 1)], [QPointF(0.5, 0.5), QPointF(2, 0.5), QPointF(2, 2), QPointF(0.5, 2)], [QPointF(-0.5, 0.5), QPointF(3, 2)], [QPointF(4, 0.5), QPointF(6, 2)], [QPointF(5, 0.5), QPointF(7, 2)]]


prepParameters(selections, 0, 0, 0, 0, 0)

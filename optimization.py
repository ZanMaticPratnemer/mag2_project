from customFuncs import *
import numpy as np
import time
import random
import copy

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
    rot = np.array([[np.cos(np.radians(-th)), -np.sin(np.radians(-th))], [np.sin(np.radians(-th)), np.cos(np.radians(-th))]])
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

def optimize(p):

    if not p.ranges:
        return


    T = 24/p.f * 60 * 60
    d_deg = 360/p.f

    print("optimize")

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

    # Find out how many of those flights we need and with what parameters
    print(flights)

    #########################
    ## Evolution algorithm ##
    #########################

    # We do not need to index all flights, because their timestamp (flight[1]) can act as an index
    

    # Calculate the optimistic number of flights needed
    _, max_width = angleToWidth(p.gamma_max, p.alpha, p.h)
    
    combined_range = 0
    for r in p.ranges:
        combined_range = combined_range + r[1] - r[0]
    n_min = int(np.ceil(float(combined_range)/float(max_width)))

    print(f"n_min: {n_min}")

    # Number of parents for the next population
    pn = 4

    # Initial population size
    ps = 1000

    # Flight mutation factor
    fmf = 1

    # Try to find a solution with n_min flights.
    # Then repeat untill we can cover the selected area
    n = n_min
    covered = False

    max_itter = 500
    

    while not covered:
        # Create an initial population.
        # Individual is a list of flights with an added element of gamma.
        # Flight time (second element in the list) can be used as an index,
        # since it is unique for all flights.
        pop = []

        # If we use all flights there is no use for flight mutation later on
        if n == len(flights):
            fmf = 0

        for i in range(ps):
            if n == len(flights):
                ind = copy.deepcopy(flights)
            else:
                ind = copy.deepcopy(random.sample(flights, k=n))
                
            for flight in ind:
                flight.append(random.uniform(-p.gamma_max, p.gamma_max))
            pop.append([ind, cost(ind, p)])



        prev_min = np.inf
        end_cond = 0

        # Main optimization loop
        for i in range(max_itter):
            parents = []
            # Get parents for a new population
            for j in range(pn):
                min_cost = np.inf
                for ind in pop:
                    if ind[1][0] < min_cost:
                        if ind in parents:
                            continue
                        min_cost = ind[1][0]
                        min_ind = ind
                min_ind[0].sort(key=lambda f: f[1])
                parents.append(min_ind)
            
            # Create a new population
            pop = []
            parents_test=[a[0] for a in parents]

            # Crossover
            if n != 1:
                for p1 in parents:
                    for p2 in parents:
                        if p1 == p2:
                            continue

                        cut = random.randrange(1, n)

                        # Crossover
                        c1 = copy.deepcopy(p1[0][:cut]) + copy.deepcopy(p2[0][cut:])
                        c2 = copy.deepcopy(p2[0][:cut]) + copy.deepcopy(p1[0][cut:])


                        # Check for duplicate flights
                        for f_new in c1[cut:]:
                            for f_old in c1[:cut]:
                                if f_new[1] == f_old[1]:
                                    new = getRandomValidFlight(flights, c1)
                                    f_new[0] = new[0]
                                    f_new[1] = new[1]
                                    f_new[2] = random.uniform(-p.gamma_max, p.gamma_max)

                        for f_new in c2[cut:]:
                            for f_old in c2[:cut]:
                                if f_new[1] == f_old[1]:
                                    new = getRandomValidFlight(flights, c2)
                                    f_new[0] = new[0]
                                    f_new[1] = new[1]
                                    f_new[2] = random.uniform(-p.gamma_max, p.gamma_max)

                        if c1 in parents_test:
                            c1[random.randrange(n)][2] = random.uniform(-p.gamma_max, p.gamma_max)
                        if c2 in parents_test:
                            c2[random.randrange(n)][2] = random.uniform(-p.gamma_max, p.gamma_max)
                            
                        pop.append([c2, np.inf])
                        pop.append([c1, np.inf])

            # pop_m = copy.deepcopy(pop)
            pop_m = []

            # Mutation
            mutf = np.random.rand(ps-pn, n)
            for j, ind in enumerate(pop):
                for k, f in enumerate(ind[0]):

                    # Mutation of flights
                    if mutf[j][k] < fmf:
                        ind_m = copy.deepcopy(ind)
                        m = getRandomValidFlight(flights, ind[0])
                        ind_m[0][k][0] = m[0]
                        ind_m[0][k][1] = m[1]
                        ind_m[0][k][2] = random.uniform(-p.gamma_max, p.gamma_max)
                        pop_m.append(ind_m)

            pop = pop + pop_m

            # Add current parents to the new population
            pop = pop + parents

            # Mildly mutate parents and add them to the population
            pop_m = []
            for ind in parents:
                for k, f in enumerate(ind[0]):
                    ind_m = copy.deepcopy(ind)
                    ind_m[0][k][2] = f[2] + random.gauss(0, 0.01)
                    pop_m.append(ind_m)


            pop = pop + pop_m

            # Calculate costs for the new population
            for ind in pop:
                ind[1] = cost(ind[0], p)
                

            min_cost = np.inf
            for ind in pop:
                if ind[1][0] < min_cost:
                    min_cost = ind[1][0]
                    min_ind = ind
            print(min_cost)

            if prev_min == min_cost and min_ind[1][2] == 0:
                end_cond = end_cond + 1
                if end_cond == 50:
                    break
            else:
                end_cond = 0
            prev_min = min_cost



            
        
        min_cost = np.inf
        for ind in pop:
            if ind[1][0] < min_cost:
                min_cost = ind[1][0]
                min_ind = ind

        if min_ind[1][1] == 0:
            print(min_ind)
            covered = True
        else:
            n = n + 1
            print(f"Staring a new optimization iteration with {n} flights used.")

    return min_ind[0]
                        





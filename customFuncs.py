import numpy as np
import time
import copy


# Transformation between geographical coordinates and internal coordinate system
x_k = 3./1294
x_n = 13.254

y_k = -1./431
y_n = 46.948

# Approx latitude
a_lat = 46.119553


# Length of a longitude degree at a_lat in kilometers
deg = (111412.84*np.cos(np.radians(a_lat)) - 93.5*np.cos(np.radians(a_lat)) + 0.118*np.cos(np.radians(a_lat))) * np.power(10., -3)

def ccw(A, B, C):
    return (C.y()-A.y())*(B.x()-A.x()) > (B.y()-A.y())*(C.x()-A.x())

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def euclDist(A, B):
    return np.sqrt(np.power(A.x() - B.x(), 2) + np.power(A.y() - B.y(), 2))

# Angle of z axis to width of picture in internal coordinate system
# Returns dist to start of the picture (from flight path) and picture width in a touple
def angleToWidth(gamma, alpha, h):
    gamma = np.radians(gamma)
    alpha = np.radians(alpha)
    c = np.tan(gamma-alpha) * h
    l = h/np.cos(gamma)
    beta = np.pi/2 - (gamma + alpha)
    phi = np.pi/2 + (gamma - alpha)
    a = l * np.sin(alpha)/np.sin(beta)
    b = l * np.sin(alpha)/np.sin(phi)

    return (geoToInx(kmToLongitude(c)+x_n), geoToInx(kmToLongitude(a + b)+x_n))

# Get input of multiple vectors
# Output the same number of vectors but with only the lowest and the highest element of input vectors
def findOuter(vectors):
    out = []
    for vector in vectors:
        min_e = np.inf
        max_e = - np.inf
        for p in vector:
            if p < min_e:
                min_e = p
            elif p > max_e:
                max_e = p
        out.append(np.array([min_e, max_e]))

    return out

def inToGeox(x):
    return x_k * float(x) + x_n 

def inToGeoy(y):
    return y_k * float(y) + y_n

def geoToInx(x):
    return (float(x) - x_n) / x_k

def geoToIny(y):
    return (float(y) - y_n) / y_k

def flightValid(pos, t, ranges, th, max_gamma, alpha, h):
    ts = time.localtime(t)
    rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
    if (ts.tm_hour >= 7 and ts.tm_hour <= 21):
        p_in = np.array([[geoToInx(pos)], [geoToIny(a_lat)]])
        p_in = rot @ p_in
        p = p_in[0][0]
        c, d = angleToWidth(max_gamma, alpha, h)
        reach = c + d

        for r in ranges:
            if np.abs(r[0] - p) < reach:
                return True

    return False

def kmToLongitude(km):
    deg = (111412.84*np.cos(np.radians(a_lat)) - 93.5*np.cos(np.radians(a_lat)) + 0.118*np.cos(np.radians(a_lat))) * np.power(10., -3)
    return km/deg

def canCover(flights_geo, p):
    ranges = copy.deepcopy(p.ranges)
    max_gamma = p.gamma_max
    alpha = p.alpha
    h = p.h
    th = p.th
    # Sort flights and ranges by position ascending
    flights_geo = sorted(flights_geo, key=lambda pos: pos[0])
    ranges = sorted(ranges, key=lambda pos: pos[0])

    rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])

    flights = []
    for flight in flights_geo:
        p_in = np.array([[geoToInx(flight[0])], [geoToIny(a_lat)]])
        p_in = rot @ p_in
        flights.append([p_in[0][0], flight[1]])

    # Area still covered by next flight
    cov_area = np.array([0, 0])

    c_max, d = angleToWidth(max_gamma, alpha, h)
    # c_max is always positive since max_gamma is always positive
    # Because of that we get reach as c_max + d
    reach_max = c_max + d

    

    for f in flights:
        if not ranges:
            return True

        r = ranges[0]

        if (r[0] - f[0] > reach_max) and (r[0] - f[0] > 0):
            continue
        elif (r[0] - f[0] < 0) and (np.abs(r[0] - f[0]) > reach_max):
            return False

        # If we cant reach the begining of the range
        # we take a picture at our max reach and only partially cover the range
        if r[0] + d - f[0] > reach_max:
            c = c_max
        # Else take the picture at the begining of the range
        else:
            c = r[0] - f[0]

        # Get the actual area we can cover
        w = cToWidth(c, alpha, h)

        # Four scenarios, but only the first two possible:
        # 1. picture area partialy overlaps with the start of a range
        # 2. picture area covers the entire range
        # 3. picture area partialy overlaps with the end of a range
        # 4. picture area is inside a range
        # 
        # Scenario 3 and 4 are not possible because we return false if
        # the leftmost picture area does not begin before or at the start of the range

        if (c+f[0] <= r[0]) and (c+w+f[0] > r[0]) and (c+w+f[0] < r[1]):
            ranges[0][0] = c+w+f[0]
        elif c+f[0] <= r[0] and (c+w+f[0] >= r[1]):
            ranges.pop(0)
            cov_area = np.array([r[1], c+w+f[0]])
            if not ranges:
                return True

            # Because the satelite takes the picture of the area beyond our first range
            # it can also cover more areas, if they are close enough. Check for that
            while cov_area[1] > ranges[0][0]:
                if (cov_area[1] > ranges[0][0]) and (cov_area[1] < ranges[0][1]):
                    ranges[0][0] = cov_area[1]
                    cov_area = np.array([0, 0])
                elif cov_area[1] >= ranges[0][1]:
                    cov_area = np.array([ranges[0][1], cov_area[1]])
                    ranges.pop(0)
                    if not ranges:
                        return True
    

    if not ranges:
        return True
    else:
        return False

            

            
def cToWidth(c, alpha, h):
    gamma = np.arctan(c/h)+alpha
    _, d = angleToWidth(gamma, alpha, h)
    return d


def cost(flights_, p):
    flights = copy.deepcopy(flights_)
    areas = copy.deepcopy(p.ranges)
    th = p.th
    alpha = p.alpha
    h = p.h

    # Biggest cost factor is the area left uncovered
    for f in flights:
        rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
        p_in = np.array([[geoToInx(f[0])], [geoToIny(a_lat)]])
        p_in = rot @ p_in
        pos = p_in[0]
        r, w = angleToWidth(f[2], alpha, h)
        for i, a in enumerate(areas):
            if not a:
                continue
            if (a[0] >= pos+r and a[0] <= pos+r+w) or (a[1] >= pos+r and a[1] <= pos+r+w):
                # Flight at least partially covers the area

                if (a[0] >= pos+r) and (a[1] <= pos+r+w):
                    # Flight completely covers the area
                    areas[i] = []
                else:
                    # Flight partially covers the area
                    if pos+r <= a[0]:
                        areas[i] = [pos+r+w, a[1]]
                    else:
                        areas[i] = [a[0], pos+r]
        
        # Clear empty areas
        try:
            while True:
                areas.pop(areas.index([]))
        except ValueError:
            pass

    # Get the sum of uncovered areas
    sum = 0
    if areas:
        # Areas is not an empty list
        # That means something is left uncovered
        for a in areas:
            sum = sum + (a[1] - a[0])




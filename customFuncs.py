import numpy as np
import time


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
# Returns dist to start of the picture (from flight path) and picture width in a list
def angleToWidth(gamma, alpha, h):
    c = np.tan(gamma-alpha) * h
    l = h/np.cos(gamma)
    beta = np.pi/2 - (gamma + alpha)
    phi = np.pi/2 + (gamma - alpha)
    a = l * np.sin(alpha)/np.sin(beta)
    b = l * np.sin(alpha)/np.sin(phi)

    return (c, a + b)

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
    if (t_s.tm_hour > 8 and t_s.tm_hour < 20):
        p_in = np.array([[geoToInx(pos)], [geoToIny(a_lat)]])
        p_in = rot @ p_in
        p = p_in[0][0]
        c, d = angleToWidth(np.abs(max_gamma), alpha, h)
        reach = c + d

        for r in ranges:
            if np.abs(r[0] - p) < reach:
                return True

    return False

def kmToLongitude(km):
    deg = (111412.84*np.cos(np.radians(a_lat)) - 93.5*np.cos(np.radians(a_lat)) + 0.118*np.cos(np.radians(a_lat))) * np.power(10., -3)
    return km/deg

def canCover(flights, ranges, max_gamma, alpha, h):
    # Sort flights and ranges by position ascending
    flights = sorted(flights, key=lambda pos: pos[0])
    ranges = sorted(ranges, key=lambda pos: pos[0])

    # Area still covered by next flight
    cov_area = np.array([0, 0])

    c_max, d = angleToWidth(max_gamma, a, h)
    if c_max < 0:
        reach_max = c_max
    else:
        reach_max = c_max + d

    for f in flights:
        if not ranges:
            return True

        r = ranges[0]

        # First check if last flight left a covered area to the right of the previous range
        while True:
            if not ranges:
                return True
            if (cov_area[0] < r[0]) and (cov_area[1] > r[0]) and (cov_area[1] < r[1]):
                ranges[0][0] = c+w+f[0]
                r = ranges[0]
                continue
            elif cov_area[0] < r[0] and (cov_area[1] > r[1]):
                ranges.pop(0)
                cov_area = np.array([r[1], cov_area[1]])
                r = ranges[0]
            break

        if not (r[0] - f[0] < reach_max):
            continue
        if c_max < 0:
            if c_max + f[0] > r[0]:
                return False
            else:
                c = r[0]
        else:
            c = min(c_max+f[0], r[0])
        w = cToWidth(c, alpha, h)

        # Four scenarios, but only the first two possible:
        # 1. picture area partialy overlaps with the start of a range
        # 2. picture area covers the entire range
        # 3. picture area partialy overlaps with the end of a range
        # 4. picture area is inside a range
        # 
        # Scenario 3 and 4 are not possible because we return false if
        # the leftmost picture area does not begin before or at the start of the range

        if (c+f[0] < r[0]) and (c+w+f[0] > r[0]) and (c+w+f[0] < r[1]):
            ranges[0][0] = c+w+f[0]
        elif c+f[0] < r[0] and (c+w+f[0] > r[1]):
            ranges.pop(0)
            cov_area = np.array([r[1], c+w+f[0]])

    if not ranges:
        return True
    else:
        return False

            

            
def cToWidth(c, alpha, h):
    gamma = np.arctan(c/h)+alpha
    _, d = angleToWidth(gamma, alpha, h)
    return d


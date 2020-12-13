import numpy as np
import time


# Transformation between geographical coordinates and internal coordinate system
x_k = 2.2907 * np.power(10.,-3)
x_n = 13.2468137

y_k = -1.5771 * np.power(10.,-3)
y_n = 47.0369964

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

# Angle of z axis to width of picture in km
# Returns dist to start of the picture and picture width in a list
def angleToWidth(gamma, alpha, h):
    c = np.tan(gamma-alpha) * h
    l = h/np.cos(gamma)
    beta = np.pi/2 - (gamma + alpha)
    phi = np.pi/2 + (gamma - alpha)
    a = l * np.sin(alpha)/np.sin(beta)
    b = l * np.sin(alpha)/np.sin(phi)

    return (geoToIny(kmToLongitude(c)+x_n), geoToIny(kmToLongitude(a + b)+x_n))

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

def flightValid(pos, t):
    ts = time.localtime(t)
    return ((t_s.tm_hour > 8 and t_s.tm_hour < 20) and (pos > 13.396613888888888-2 and pos < 16.60213611111111+2))

def kmToLongitude(km):
    deg = (111412.84*np.cos(np.radians(a_lat)) - 93.5*np.cos(np.radians(a_lat)) + 0.118*np.cos(np.radians(a_lat))) * np.power(10., -3)
    return km/deg

import numpy as np

# alpha = np.arctan2(5,515)
alpha = np.radians(1)

h = 515

def ccw(A, B, C):
    return (C.y()-A.y())*(B.x()-A.x()) > (B.y()-A.y())*(C.x()-A.x())

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def euclDist(A, B):
    return np.sqrt(np.power(A.x() - B.x(), 2) + np.power(A.y() - B.y(), 2))

# Length of a degree longtitude at "lat" latitude
def longDegAtLat(lat):
    return (111412.84*np.cos(np.radians(lat)) - 93.5*np.cos(np.radians(3*lat)) + 0.118*np.cos(np.radians(5*lat)))

# Angle of z axis to width of picture in km
# Returns dist to start of the picture and picture width in a list
def angleToWidth(gamma):
    c = np.tan(gamma-alpha) * h
    l = h/np.cos(gamma)
    beta = np.pi/2 - (gamma + alpha)
    phi = np.pi/2 + (gamma - alpha)
    a = l * np.sin(alpha)/np.sin(beta)
    b = l * np.sin(alpha)/np.sin(phi)

    return [c, a + b]
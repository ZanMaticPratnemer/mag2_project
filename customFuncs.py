import numpy as np


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

    return [c, a + b]

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
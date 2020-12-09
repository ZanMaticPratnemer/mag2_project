import numpy as np

def ccw(A, B, C):
    return (C.y()-A.y())*(B.x()-A.x()) > (B.y()-A.y())*(C.x()-A.x())

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def euclDist(A, B):
    return np.sqrt(np.power(A.x() - B.x(), 2) + np.power(A.y() - B.y(), 2))
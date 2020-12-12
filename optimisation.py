from customFuncs import *
import numpy as np

# TODO: remove after testing
from PyQt5.QtCore import QPoint

def optimisation(sel, th, f, h, alpha, gamma):

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
    # This way path of flight is aligned with y axis and we only have to potimize number of flights used and their angle of recording
    rot = np.array([[np.cos(-th), -np.sin(-th)], [np.sin(-th), np.cos(-th)]])
    print(rot)
    for i, area in enumerate(areas):
        print(rot @ area)


selections = [[QPoint(0, 0), QPoint(1, 0), QPoint(1, 1), QPoint(0, 1)], [QPoint(1, 1), QPoint(602, 497), QPoint(697, 497), QPoint(697, 387)]]


optimisation(selections, np.pi/2, 0, 0, 0, 0)

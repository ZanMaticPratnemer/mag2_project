import numpy as np
import matplotlib.pyplot as plt
import os
os.environ['PROJ_LIB'] = r'C:\\Users\\zanma\\anaconda3\\pkgs\\proj-7.2.0-h3e70539_0\\Library\\share'
from mpl_toolkits.basemap import Basemap
from itertools import chain

def draw_map(m, scale=0.2):
    # draw a shaded-relief image
    m.drawcountries()
    m.drawcoastlines(linewidth=0.5)
    
    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.arange(45.5, 46.75, 0.5))
    lons = m.drawmeridians(np.arange(13, 17, 0.5))

    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)
    
    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='black')


fig = plt.figure(figsize=(8, 6), edgecolor='w')
m = Basemap(projection='cyl', resolution='f',
            llcrnrlat=45.38, urcrnrlat=46.95,
            llcrnrlon=13.25, urcrnrlon=16.7, )
draw_map(m)

plt.show()
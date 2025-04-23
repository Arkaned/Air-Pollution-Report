
# this file allows us to plot the first time step of data

# pip install pygrib==2.1.6 matplotlib basemap numpy

import pygrib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
import numpy as np
import os

plt.figure(figsize=(12, 8))

grib_folder = 'Copernicus_datasets'
grib = os.path.join(grib_folder, '5bb270cf84365703ee359cae8eeea540.grib')

grbs = pygrib.open(grib)

grb = grbs.select()[0]
data = grb.values

# need to shift data grid longitudes from (0..360) to (-180..180)
lons = np.linspace(float(grb['longitudeOfFirstGridPointInDegrees']), \
    float(grb['longitudeOfLastGridPointInDegrees']), int(grb['Ni']) )
lats = np.linspace(float(grb['latitudeOfFirstGridPointInDegrees']), \
    float(grb['latitudeOfLastGridPointInDegrees']), int(grb['Nj']) )
#data, lons = shiftgrid(180., data, lons, start=False)
grid_lon, grid_lat = np.meshgrid(lons, lats) # regularly spaced 2D grid

m = Basemap(projection='cyl', 
            llcrnrlon=lons.min(),
            urcrnrlon=lons.max(), 
            llcrnrlat=lats.min(),
            urcrnrlat=lats.max(), 
            resolution='c'
            )

x, y = m(grid_lon, grid_lat)

cs = m.pcolormesh(x, y, data, cmap=plt.cm.gist_stern_r)

m.drawcoastlines()
m.drawmapboundary()
m.drawparallels(np.arange(-90., 120.,30.),labels=[1,0,0,0])
m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

plt.colorbar(cs, orientation='vertical', shrink=0.5)
plt.title('North Africa particles')
plt.savefig(grib+'.png')

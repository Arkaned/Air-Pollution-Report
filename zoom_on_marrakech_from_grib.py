# this file allows us to animate the time steps of the data:


# pip install pygrib==2.1.6 matplotlib basemap numpy

import pygrib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import numpy as np
import os

grib_folder = 'Copernicus_datasets'
grib = os.path.join(grib_folder, '5bb270cf84365703ee359cae8eeea540.grib')
grbs = pygrib.open(grib)
grb_list = grbs.select()

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(bottom=0.2)

def create_basemap(lons, lats):
    m = Basemap(projection='cyl', 
                llcrnrlon=lons.min(),
                urcrnrlon=lons.max(), 
                llcrnrlat=lats.min(),
                urcrnrlat=lats.max(), 
                resolution='c'
                )
    return m

# extract lons/lats from the first frame
grb0 = grb_list[0]
lons = np.linspace(float(grb0['longitudeOfFirstGridPointInDegrees']),
                   float(grb0['longitudeOfLastGridPointInDegrees']), int(grb0['Ni']))
lats = np.linspace(float(grb0['latitudeOfFirstGridPointInDegrees']),
                   float(grb0['latitudeOfLastGridPointInDegrees']), int(grb0['Nj']))
grid_lon, grid_lat = np.meshgrid(lons, lats)

# Find the global min/max for all timesteps
all_min = np.inf
all_max = -np.inf
for grb in grb_list:
    data=grb.values
    all_min = min(all_min, np.nanmin(data))
    all_max = max(all_max, np.nanmax(data))
    
print(f"Global colorbar range: {all_min:.2f} to {all_max:.2f}")

# Create basemap
m = create_basemap(lons, lats)
x, y = m(grid_lon, grid_lat)

# initial plot
data = grb0.values
cs = m.pcolormesh(x, y, data, cmap=plt.cm.gist_stern_r, vmin=all_min, vmax=all_max)
    
m.drawcoastlines()
m.drawmapboundary()
m.drawcountries()
m.drawparallels(np.arange(-90., 120.,30.),labels=[1,0,0,0])
m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

colorbar = plt.colorbar(cs, orientation='vertical')
title = plt.title(f'PM Concentration on {grb0.validDate}')

# Create the slider:
ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
slider = Slider(
    ax=ax_slider,
    label='Timestep',
    valmin=0,
    valmax=len(grb_list) - 1,
    valinit=0,
    valstep=1
)

def update(val):
    idx = int(slider.val)
    grb = grb_list[idx]
    data = grb.values
    
    cs.set_array(data.ravel()) # update the color mesh data
    #cs.set_clim(vmin=data.min(), vmax=data.max()) # update color limits
    title.set_text(f'PM Concentration on {grb.validDate}')
    fig.canvas.draw_idle()
    
slider.on_changed(update)

plt.show()

print("done!")
#plt.savefig(grib+'.png')
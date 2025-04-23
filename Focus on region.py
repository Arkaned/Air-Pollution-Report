# this file creates a system for showing the boundaries within morroco (or at least the boundaries of marakkesh as that is our main focus)
# This file also teaches how to give cool background (more visible when colormesh alpha is lower)



import pygrib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import numpy as np
import os
# pip install pyshp
import shapefile

grib_folder = 'Copernicus_datasets'
grib = os.path.join(grib_folder, '5bb270cf84365703ee359cae8eeea540.grib')
grbs = pygrib.open(grib)
grb_list = grbs.select()

print(grb_list)

fig, ax = plt.subplots(figsize=(12, 8))
plt.subplots_adjust(bottom=0.2)

def create_basemap(lons, lats):
    m = Basemap(projection='cyl', 
                llcrnrlon=lons.min(),
                urcrnrlon=lons.max(), 
                llcrnrlat=lats.min(),
                urcrnrlat=lats.max(),
                
                #llcrnrlon=-8.5,
                #urcrnrlon=-7.7, 
                #llcrnrlat=31.3,
                #urcrnrlat=32.1,
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

#m.drawcoastlines()
#m.drawmapboundary()
#m.drawcountries()
#m.drawrivers()
#m.drawparallels(np.arange(-90., 120.,30.),labels=[1,0,0,0])
#m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

m.arcgisimage(service='World_Imagery', xpixels=800, verbose=True)
#m.etopo()
#m.drawcoastlines()
x, y = m(grid_lon, grid_lat)

# initial plot
data = grb0.values

cs = m.pcolormesh(x, y, data, cmap=plt.cm.gist_stern_r, vmin=all_min, vmax=all_max, alpha=0) # lowered this to effectively remove it

sf = shapefile.Reader('Morocco-Counties-shapefile/maroc_wgs')
sf.encoding = 'latin-1'

m.readshapefile('Morocco-Counties-shapefile/maroc_wgs', 'provinces', drawbounds=True, default_encoding='latin-1')

# Then loop through shapes and highlight only Marrakech
for info, shape in zip(m.provinces_info, m.provinces):
    #print(info)
    
    if info['Province'] == 'Marrakech': # depending on shapefile attribute names
        poly = plt.Polygon(shape, facecolor='none', edgecolor='red', linewidth=2)
        ax.add_patch(poly)
        
        shape_array = np.array(shape)  # convert list to numpy array
        min_lon = shape_array[:, 0].min()
        max_lon = shape_array[:, 0].max()
        min_lat = shape_array[:, 1].min()
        max_lat = shape_array[:, 1].max()
        
        print(f"Marrakech Bounding Box:")
        print(f"Longitude: {min_lon:.4f} to {max_lon:.4f}")
        print(f"Latitude: {min_lat:.4f} to {max_lat:.4f}")
        
        
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
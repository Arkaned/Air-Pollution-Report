# This file works on isolating marrakech from the rest, making the data variability in marakesh more visible in this map.
# change of plans, this focuses on just getting the data from the grib that is close enough to Rue de Temple to matter (31.626635, -8.001758)


import pygrib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import shiftgrid
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import numpy as np
import os
#from osgeo import gdal
import rasterio
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from statsmodels.nonparametric.smoothers_lowess import lowess
from numerize import numerize
import matplotlib
#import plotly.express as px
# pip install pyshp
#from osgeo import shapefile


grib_folder = 'Copernicus_datasets'
grib = os.path.join(grib_folder, '5bb270cf84365703ee359cae8eeea540.grib')
'''
# the following code for now only works in gosgeo4w shell
arq1 = gdal.Open(grib)
GT_entrada = arq1.GetGeoTransform()
print(GT_entrada)

save_arq = gdal.Translate('tif_file.tif’,arq1)

with rasterio.open('tif_file.tif') as tiffile:
    print(tiffile.crs)
'''


## -------------- attempting to follow tutorial https://metview.readthedocs.io/en/latest/examples/analysing_data.html

grbs = pygrib.open(grib)
grb_2_5_list = grbs.select(name='Particulate matter d < 2.5 um')
grb_10_list = grbs.select(name='Particulate matter d < 10 um')
# let's create datasets for both lists including data, and time as main characters
data_pm_10 = []
dates_pm_10 = []
B = 1000000000 # multiply by a billion to get micrograms
for grb in grb_10_list:
    #print(grb)
    data, lats, lons = grb.data(lat1=31.3, lat2=32.1, lon1=-8.5, lon2=-7.7) # these should be made into constants outside this loop
    #print(data, lats, lons)
    #print(np.mean(data), grb.dataDate)
    data_pm_10.append(np.mean(data) * B)
    
    # splitting the date into something more readable down the line
    strDate = str(grb.dataDate)
    dates_pm_10.append(strDate[:4] + '-' + strDate[4:6] + '-' + strDate[6:8])
    
data_pm_2_5 = []
dates_pm_2_5 = []

for grb in grb_2_5_list:
    data, lats, lons = grb.data(lat1=31.3, lat2=32.1, lon1=-8.5, lon2=-7.7)
    
   # print(data, lats, lons)
    #print(np.mean(data), grb.dataDate)
    data_pm_2_5.append(np.mean(data) * B)
    # splitting the date into something more readable down the line
    strDate = str(grb.dataDate)
    dates_pm_2_5.append(strDate[:4] + '-' + strDate[4:6] + '-' + strDate[6:8])

# cool, let's change the time series to be a bit more readable:


df = pd.DataFrame({
    "data_pm_2.5":data_pm_2_5,
    "dates_pm_2.5":dates_pm_2_5,
    "data_pm_10":data_pm_10,
    #"dates_pm_10":dates_pm_10
})

#print(df['data_pm_2.5'].dropna())
df["dates_pm_2.5"] = pd.to_datetime(df["dates_pm_2.5"])

df = df.groupby(df["dates_pm_2.5"].dt.date).mean()
df.index = pd.to_datetime(df.index)
print(df)

# great, now that we have this dataset organized, it's time to plot it linearly over time!

#fig = px.line(df, x='dates_pm_2.5', y=['data_pm_2.5', 'data_pm_10'])
#fig.show()


#sns.set(style="whitegrid")
#plt.figure(figsize=(12, 6))



#df.plot()
#sns.lineplot(data=df, x='dates_pm_2.5', y='data_pm_2.5')
#sns.lineplot(data=df)
matplotlib.rcParams.update({'font.size': 22})


dates_numeric = mdates.date2num(df['dates_pm_2.5'])

pm10_smooth = lowess(df['data_pm_10'], dates_numeric, frac=0.01)
pm2_5_smooth = lowess(df['data_pm_2.5'], dates_numeric, frac=0.01)

fig, ax = plt.subplots()
ax.plot(df["dates_pm_2.5"], df["data_pm_10"], label="PM < 10", alpha=0.5, color="blue", linewidth=0.5)
ax.plot(df["dates_pm_2.5"], df["data_pm_2.5"], label="PM < 2.5", alpha=0.7, color="orange", linewidth=0.5)
#date_format = DateFormatter("%y")
#ax.xaxis.set_major_formatter(date_format)

ax.plot(mdates.num2date(pm10_smooth[:, 0]), pm10_smooth[:, 1], "--", label="PM < 10 μm (trend)", color="blue", linewidth=2)
ax.plot(mdates.num2date(pm2_5_smooth[:, 0]), pm2_5_smooth[:, 1], "--", label="PM < 2.5 μm (trend)", color="red", linewidth=2)

ax.set(ylabel='particulate atmospheric concentration (μg $m^{-3}$)')


ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

ax.spines[['right', 'top']].set_visible(False)

#plt.plot(df['data_pm_2.5'], label='pm < 2.5', color='blue')
#plt.plot(df['data_pm_10'], label='pm < 10', color='green')

# show when covid 
ax.axvline(pd.Timestamp('2020-03-20'), color='black', linestyle='-.', linewidth=1, label="Covid-19 lockdown in Morocco")
ax.axvline(pd.Timestamp('2022-10-03'), color='black', linestyle='dotted', linewidth=2, label="end of Covid-19 stringent travel rules")



ax.legend(fontsize=16) #loc='center left', bbox_to_anchor=(1, 0.5)

plt.tight_layout()
#plt.xticks(rotation=30)

#plt.xticks(pd.date_range(start=df['dates_pm_2.5'][0], end="", freq="M"))

plt.show()
#plt.plot(df['data_pm_2.5'])











## ----------------------



'''

grbs = pygrib.open(grib)
grb_list = grbs.select()

grbs.seek(0)
# print(grbs.read()) this call is quite messy

selected_grb = grbs.select(name='Particulate matter d < 2.5 um')[0]
data_actual, lats, lons = selected_grb.data()

#print(data_actual, lats, lons)
#print(type(data_actual))

data_extract = np.ma.getdata(data_actual, subok=True)

#print("data_extract: ", data_extract)

mask_extract = np.ma.getmask(data_actual)

#print(mask_extract)

# a more structured way of opening it up is through:
#for grb in grbs[1:100]:
#    
#    #print(grb.data())
#    selected_grb = grb.select(name='Particulate matter d < 2.5 um')
#    data_actual, lats, lons = selected_grb.data()
#    print(data_actual, lats, lons)
    
    #print(grb)
    #print("values: ", grb.values)
    #print("val length: ", len(grb.values))
    
    
    #print("latlons: ", grb.latlons()[1])
    #print("latlon length: ", len(grb.latlons()[1]))
    #print()

'''


'''
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

#m.drawcoastlines()
#m.drawmapboundary()
#m.drawcountries()
#m.drawrivers()
#m.drawparallels(np.arange(-90., 120.,30.),labels=[1,0,0,0])
#m.drawmeridians(np.arange(-180.,180.,60.),labels=[0,0,0,1])

m.arcgisimage(service='World_Shaded_Relief', xpixels=3000, verbose=True)

x, y = m(grid_lon, grid_lat)

# initial plot
data = grb0.values

cs = m.pcolormesh(x, y, data, cmap=plt.cm.gist_stern_r, vmin=all_min, vmax=all_max, alpha=0.8)

m.readshapefile('Morocco-Counties-shapefile/maroc_wgs', 'provinces', drawbounds=True, default_encoding='latin-1')

# Then loop through shapes and highlight only Marrakech
for info, shape in zip(m.provinces_info, m.provinces):
    #print(info)
    
    if info['Province'] == 'Marrakech': # depending on shapefile attribute names
        poly = plt.Polygon(shape, facecolor='none', edgecolor='red', linewidth=2)
        ax.add_patch(poly)
        
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

'''
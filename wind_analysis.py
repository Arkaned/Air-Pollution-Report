import pygrib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import math
from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib

grib = 'wind_data.grib'
grbs = pygrib.open(grib)
grbs.seek(0)

u_wind_data = grbs.select(name='10 metre U wind component')
v_wind_data = grbs.select(name='10 metre V wind component')

for grb in grbs[1:10]:
    print(grb)
    # just to get a good understanding of the labels and such

dates = []
uWind = []
for grb in u_wind_data:
    data, lats, lons = grb.data()
    strDate = str(grb.dataDate)
    uWind.append(np.mean(data))
    dates.append(strDate[:4] + '-' + strDate[4:6] + '-' + strDate[6:8])

vWind = []
for grb in v_wind_data:
    data, lats, lons = grb.data()
    vWind.append(np.mean(data))

print("length of wind data", len(uWind))
# yeah wind data is double the size it needs to be:
cutWind = pd.DataFrame({
    'date': dates,
    'uWind':uWind,
    'vWind':vWind
})
print(cutWind)
# group by date and average u and v:
daily_avg = cutWind.groupby('date').agg({
    'uWind':'mean',
    'vWind':'mean'
}).reset_index()
#print(daily_avg)


# use numpy to calculate direction
theta_rad = np.arctan2(-daily_avg['uWind'], -daily_avg['vWind'])
theta_deg = np.degrees(theta_rad)
wind_dir = (theta_deg + 360) % 360

windSpeed = np.sqrt(np.power(daily_avg['uWind'],2) + np.power(daily_avg['vWind'], 2))

daily_avg['wind_direction_deg'] = wind_dir

print(daily_avg)

# time to bin these directions:
def wind_direction_label(wind_dir):
    bins = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N']
    edges = [0, 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5, 360.0]
    
    # use pandas cut function
    labels = pd.cut((wind_dir%360), 
                    bins=edges, # start slightly below 0 to catch 0 correctly
                    labels=bins,
                    right=False, # includes left endpoint, excludes right
                    ordered = False # this solves the duplicate label issue
                    ) 
    return labels
    
wind_dir_labels = wind_direction_label(wind_dir)

windDF = pd.DataFrame({
    "date":daily_avg['date'],
    "uWind":daily_avg['uWind'],
    "vWind":daily_avg['vWind'],
    "wind_dir_deg":wind_dir,
    "wind_dir_labels":wind_dir_labels,
    "wind_speed":windSpeed
})

print(windDF)

#windDF['date'] = pd.to_datetime(windDF["date"])

# fix double date detail by creating a mean:
#windDF = windDF.groupby(windDF["date"].dt.date).mean()
#probaly not the most efficient way to do this tbh

matplotlib.rcParams.update({'font.size': 22})
windDF.index = windDF['date']
windDF.index = pd.to_datetime(windDF.index)
windDF['date'] = pd.to_datetime(windDF['date'])
#windDF = windDF.drop(windDF['date'])

print(windDF)

dates_numeric = mdates.date2num(windDF['date'])

wind_smooth = lowess(windDF['wind_speed'], dates_numeric, frac=0.1)

fig, ax = plt.subplots()
ax.plot(windDF["date"], windDF['wind_speed'], label="wind speed daily trend", color="blue", alpha=0.5, linewidth=0.5)

ax.plot(mdates.num2date(wind_smooth[:, 0]), wind_smooth[:, 1], "--", label = "wind speed LOWESS trend", color="blue", linewidth=2)

ax.set(ylabel='wind speed (m $s^{-1}$)')

ax.spines[['right', 'top']].set_visible(False)

ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

ax.legend()
plt.show()


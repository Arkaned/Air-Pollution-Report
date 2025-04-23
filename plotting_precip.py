import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import glob
from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.dates as mdates
import matplotlib as mpl

filepaths = glob.glob('precipitation_data/*.nc')
filepaths.sort()

all_precip = []
all_dates = []

for fp in filepaths:
    ds = xr.open_dataset(fp)
    precip = ds['precip']
    
    # Calculate mean precipitation for each time step (mean across lat and lon)
    mean_precip = precip.mean(dim=["latitude", "longitude"])
    
    all_precip.extend(mean_precip.values.flatten())
    all_dates.extend(mean_precip['time'].values)

# Convert the collected dates and precipitation to a pandas DataFrame
df = pd.DataFrame({
    "time": pd.to_datetime(all_dates),
    "precipitation": all_precip
})

# Step 1: Resample to monthly means using 'ME' for monthly end
df.set_index('time', inplace=True)  # Set 'time' as the index for resampling
monthly_mean = df.resample('ME').mean()  # Resample and compute the mean for each month
monthly_std = df.resample('ME').std()

# Only upper error (standard deviation)
upper_error = monthly_std['precipitation']

# Set lower error to zero
lower_error = np.zeros_like(upper_error)

# Combine into asymmetric error bar format
asymmetric_error = [lower_error, upper_error]

# Step 2: Apply LOWESS to smooth the data
lowess_result = lowess(monthly_mean['precipitation'], mdates.date2num(monthly_mean.index), frac=0.1)  # Apply LOWESS

plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')

# Step 3: Plot the monthly bar graph for the actual data and the LOWESS curve
plt.figure(figsize=(12,6)) # , facecolor='#033a73'

mpl.rcParams.update({'font.size': 22})


# Plot monthly bars for precipitation
plt.bar(monthly_mean.index, 
        monthly_mean['precipitation'], 
        width=20, 
        yerr=asymmetric_error,
        capsize=5,
        label="Monthly Mean Precipitation", 
        color='deepskyblue', 
        alpha=0.6)

# Plot the LOWESS smoothed trend, converting back to datetime for plotting
plt.plot(mdates.num2date(lowess_result[:, 0]), lowess_result[:, 1], label="monthly precipitation trend", color='white', linestyle='--', linewidth=2)

ax = plt.gca()  #
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

#ax.set_facecolor("#033a73")
#ax.grid(False)
ax.spines['bottom'].set_visible(True)
ax.spines['left'].set_visible(True)
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['axes.spines.top'] = False

# Add labels and title
#plt.xlabel('Time')
plt.ylabel('Precipitation (mm/month)')
#plt.title('Monthly Mean Precipitation')



plt.legend()
plt.grid()

# Show the plot
plt.show()
import streamlit as st
import solposx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.title("Interactive sunpath diagram")

tz = 'UTC'
times = pd.date_range('2019-01-01 00:00:00', periods=8760, freq='h', tz=tz)

def sunpath_chart(times, latitude, longitude):
    solpos = solposx.solarposition.noaa(times, latitude, longitude)
    # remove nighttime
    solpos = solpos.loc[solpos['elevation'] > 0, :]

    fig, ax = plt.subplots(figsize=(10, 4))
    points = ax.scatter(solpos['azimuth'], solpos['elevation'], s=2,
                        c=solpos.index.dayofyear, label=None,
                        cmap='twilight_shifted_r')
    # add and format colorbar
    cbar = fig.colorbar(points)
    times_ticks = pd.date_range('2019-01-01', '2020-01-01', freq='MS', tz=tz)
    cbar.set_ticks(ticks=times_ticks.dayofyear, labels=[], minor=False)
    cbar.set_ticks(ticks=times_ticks.dayofyear+15,
                   labels=times_ticks.strftime('%b'),
                   minor=True)
    cbar.ax.tick_params(which='minor', width=0)

    for hour in np.unique(solpos.index.hour):
        # choose label position by the largest elevation for each hour
        subset = solpos.loc[solpos.index.hour == hour, :]
        height = subset['elevation']
        pos = solpos.loc[height.idxmax(), :]
        azimuth_offset = -10 if pos['azimuth'] < 180 else 10
        ax.text(pos['azimuth']+azimuth_offset, pos['elevation'],
                str(hour).zfill(2), ha='center', va='bottom')

    for date in pd.to_datetime(['2019-03-21', '2019-06-21', '2019-12-21']):
        times2 = pd.date_range(date, date+pd.Timedelta('24h'), freq='5min', tz=tz)
        solpos = solposx.solarposition.noaa(times2, latitude, longitude)
        solpos = solpos.loc[solpos['elevation'] > 0, :]
        label = date.strftime('%d %b')
        ax.plot(solpos['azimuth'], solpos['elevation'], label=label)

    ax.figure.legend(loc='upper center', bbox_to_anchor=[0.45, 1], ncols=3)
    ax.set_xlabel('Solar Azimuth (degrees)')
    ax.set_ylabel('Solar Elevation (degrees)')
    ax.set_xticks([0, 90, 180, 270, 360])
    ax.set_ylim(0, 90)
    plt.xlim(0, 360)
    return fig

latitude = st.slider(
    "Select Latitude",
    min_value=-90.0,
    max_value=90.0,
    value=0.0,
    step=0.1,
)

# Longitude slider (-180 to 180 degrees)
longitude = st.slider(
    "Select Longitude",
    min_value=-180.0,
    max_value=180.0,
    value=0.0,
    step=0.1,
)

# Create and display the plot
fig = sunpath_chart(times, latitude, longitude)
st.pyplot(fig)

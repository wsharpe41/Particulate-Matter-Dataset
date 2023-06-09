import requests
import datetime
from pydantic import BaseModel
import matplotlib.pyplot as plt
import imageio
import matplotlib as mpl
import numpy as np
from PIL import Image
import cartopy.crs as ccrs
import cartopy
import os
from build_data.build_dataset import get_elevation
from time import sleep

measurement_limit = 750
last_meas = datetime.datetime.now() - datetime.timedelta(days=10)
first_meas = last_meas - datetime.timedelta(days=10)

def set_measurement_time(start):
    global last_meas
    global first_meas
    last_meas = start
    first_meas = last_meas - datetime.timedelta(days=10)

class Measurement(BaseModel):
    timestamp: datetime.datetime
    value: float
    temp_2m: float = None
    rh_2m: float = None
    rain: float = None
    wind_dir_10m: float = None
    wind_dir_100m: float = None
    wind_speed_10m: float = None
    wind_speed_100m: float = None
    wind_gusts_10m: float = None
    
class Site(BaseModel):
    site_id: str
    lat: float
    lon: float
    measurements: list[Measurement]
    elevation: float = None
    

    @classmethod
    def fetch_sites(cls, country_code, limit):
        print(f"Getting data from {first_meas} to {last_meas}")
        #UPDATE ME
        url = f"https://api.openaq.org/v2/locations?country={country_code}&limit={limit}&parameter_id=2&parameter=pm25"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error getting site data: {response.status_code}")
            print(f"Error message: {response.text}")
            return []
        response_data = response.json()["results"]
        
        sites = []
        i = 0
        for result in response_data:
            if i % 100 == 0:
                print(f"Getting site {i}")
            parameters = result["parameters"]
            last_updated = datetime.datetime.strptime(result["lastUpdated"], "%Y-%m-%dT%H:%M:%S+00:00")
            # if last_updated is before the last measurement, skip this site
            if last_updated > last_meas:
                pm25_parameter = next((param for param in parameters if param["parameter"] == "pm25"), None)
                if pm25_parameter:
                    loc = f"{result['coordinates']['latitude']},{result['coordinates']['longitude']}"
                    measurements = cls.fetch_measurements(loc,result["id"])
                    # API only allows 5 calls per second, sleep for 0.05 seconds between calls
                    sleep(.05)
                    if len(measurements) == 0:
                        #print(f"No measurements for site {result['id']}")
                        i+=1
                        continue 
                    site = cls(
                        site_id=result["id"],
                        lat=result["coordinates"]["latitude"],
                        lon=result["coordinates"]["longitude"],
                        measurements=measurements
                    )
                    sites.append(site)
            i += 1
        print(f"Got {len(sites)} sites")
        return sites

    @staticmethod
    def fetch_measurements(loc,id, measurement_limit=measurement_limit):
        url = f"https://api.openaq.org/v2/measurements"
        headers = {"Accept": "application/json"}
        #current = datetime.datetime.now()
        #first_meas = current - datetime.timedelta(days=20)
        
        params = {
            "date_from": first_meas,
            "date_to": last_meas,
            "limit": measurement_limit,
            "page": 1,
            "offset": 0,
            "sort": "desc",
            "parameter_id": 2,
            "parameter": "pm25",
            "coordinates": loc,
            "location_id":id,
            "radius": 1,
            "order_by": "datetime"
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error getting measurement data: {response.status_code} for {loc}")
            print(f"Error message: {response.text}")
            return []
        response_data = response.json()["results"]
        measurements = []
        for result in response_data:
            measurement = Measurement(
                timestamp=datetime.datetime.strptime(result["date"]["utc"], "%Y-%m-%dT%H:%M:%S+00:00"),
                value=result["value"]
            )
            measurements.append(measurement)
        
        return measurements

# Specify the country code and limit for the API call
def get_sites(limit) -> list[Site]:
    country_code = "US"
    # Fetch the sites
    sites = Site.fetch_sites(country_code, limit)
    return sites

def create_mp4(sites):
    #latitude_center = 39.8283
    #longitude_center = -98.5795
    print("CREATING MAP")
    frames = []
    projection = ccrs.PlateCarree()
    current = datetime.datetime.now()
    first_meas = current - datetime.timedelta(days=20)

    hours = []
    while first_meas < current:
        hours.append(first_meas)
    first_meas = first_meas + datetime.timedelta(hours=1)
    #for j in range(0,measurement_limit):
    j = 0
    for hour in hours:
        print(hour)
        # Create a copy of the map to update for each measurement
        fig, ax = plt.subplots(figsize=(10, 6),subplot_kw={'projection': projection})

        # Plot the measurement data on the map
        # Assuming you have latitude and longitude values in the measurement data
        latitudes = []
        longitudes = []
        values = []

        for site in sites:
            measurments = site.measurements
            for meas in measurments:
                # Get the measurement closest to the hour
                # This currently always picks the first measurement
                if abs(meas.timestamp - hour) < datetime.timedelta(hours=1):
                    latitudes.append(site.lat)
                    longitudes.append(site.lon)
                    values.append(meas.value)
                    break

        if len(values) < measurement_limit/5:
            print("Not Enough Data")
            continue
        
        # Customize the marker color based on measurement values
        colors = []
        for value in values:
            if value <= 0:
                colors.append('blue')
            elif value >= 100:
                colors.append('red')
            else:
                # Linearly interpolate between blue and red based on the measurement value
                normalized_value = (value - 0) / (100 - 0)
                red = int(255 * normalized_value)
                blue = int(255 * (1 - normalized_value))
                colors.append('#{:02x}00{:02x}'.format(red, blue))  # Hex color code

        # Plot the markers on the map
        ax.scatter(longitudes, latitudes, color=colors, s=50, alpha=0.7)

        # Set the axis labels, title, etc. as needed
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        #ax.set_title('Measurements Map')
        
        # Add time to the title without minutes and seconds
        ax.set_title(f'PM2.5 Value Map for {hour.strftime("%Y-%m-%d %H:%M")}')
        
        # Add colorbar to map
        # Create a color gradient based on the measurements
        min_measurement = 0
        max_measurement = 100
        norm = plt.Normalize(min_measurement, max_measurement)
        cmap = plt.cm.get_cmap('coolwarm')
        # Create a colorbar
        cbar = plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), orientation='horizontal', shrink=0.5)
        cbar.set_label('PM2.5 Value')


        # Draw coastlines and borders
        ax.coastlines(resolution='10m', color='black', linewidth=1)
        ax.add_feature(cartopy.feature.BORDERS, linestyle='-', linewidth=0.5)
        # Customize the map appearance if desired (e.g., background, grid, etc.)
        fig.savefig(f'frame_{j}.png')

        # Close the figure to release memory
        plt.close(fig)

        # Open the saved image using PIL
        image = Image.open(f'frame_{j}.png')

        # Append the image to the frames list
        frames.append(image)
        j+=1

    # Create a GIF from the saved frames using imageio
    # Make the GIF show each frame for 1 second
    imageio.mimsave('animation.gif', frames, duration=0.2)
    #imageio.mimsave('animation.gif', frames)

    # Create a video from the saved frames using imageio
    imageio.mimsave('animation.mp4', frames,fps=10)

    # Delete the saved frames
    for j in range(0,len(hours)):
        os.remove(f'frame_{j}.png')
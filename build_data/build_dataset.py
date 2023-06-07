import requests
import pandas as pd

def get_elevation(sites):
    locations = ""
    for site in sites:
        # Don't add the last pipe
        if site == sites[-1]:
            locations += f"{site.lat},{site.lon}"
        else:
            locations += f"{site.lat},{site.lon}|"
    
    url = 'https://api.open-elevation.com/api/v1/lookup'
    # Example Location format: locations = '10,10|20,20|41.161758,-8.583933'
    params = {
        'locations': locations
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error getting elevation data: {response.status_code}")
        return sites
    # one approach is to use pandas json functionality:
    elevation = response.json()['results']
    # Add elevation to each site (CHECK THIS WORKS)
    for i in range(0, len(sites)):
        sites[i].elevation = elevation[i]['elevation']
    return sites

def get_environmental_vars(sites: list) -> list:
    # Add RH
    # Add wind speed
    #url = "https://archive-api.open-meteo.com/v1/archive"
    j = 0
    for site in sites:
        # Get first and last measurement dates as ISO6=8601 strings without timezone
        # Temp is in C, RH is in %, Rain is in mm, Wind speed is in m/s
        site_meas = site.measurements
        if len(site_meas) == 0:
            continue
        first_meas = str(site_meas[0].timestamp.isoformat().split("T")[0])
        last_meas = str(site_meas[-1].timestamp.isoformat().split("T")[0])
        # Take only 4 decimal places for lat and lon
        lat = format(f"{site.lat:.4f}")
        lon = format(f"{site.lon:.4f}")
        if site.elevation is None:
            site_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={first_meas}&end_date={last_meas}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,windspeed_100m,winddirection_10m,winddirection_100m,windgusts_10m,rain"
        else:
            site_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={first_meas}&end_date={last_meas}&elevation{site.elevation}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,windspeed_100m,winddirection_10m,winddirection_100m,windgusts_10m,rain"
            
        response = requests.get(site_url)
        #params = {
        #    "latitude": lat,
        #    "longitude": lon,
            #"hourly": ["temperature_2m","relativehumidity_2m","rain","winddirection_10m","winddirection_100m","windspeed_10m","windspeed_100m"],
        #    "start_date" : first_meas,
        #    "end_date" : last_meas,
            #"elevation": site.elevation,
            #"windspeed_unit": "ms"
        #}
        #response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error getting data: {response.status_code}")
            return []
        response_data = response.json()
        for meas in site_meas:
            if meas == site_meas[0]:
                print(f"Getting environmental variables for site {j}")
            # Get the difference in hours between the first measurement and the current measurement
            diff = int((meas.timestamp - site_meas[0].timestamp).total_seconds() / 3600)
            # diff is the index of the measurement in the response_data
            meas.temp_2m = response_data['hourly']["temperature_2m"][diff]
            meas.rh_2m = response_data['hourly']["relativehumidity_2m"][diff]
            meas.rain = response_data['hourly']["rain"][diff]
            meas.wind_dir_10m = response_data['hourly']["winddirection_10m"][diff]
            meas.wind_dir_100m = response_data['hourly']["winddirection_100m"][diff]
            meas.wind_speed_10m = response_data['hourly']["windspeed_10m"][diff]
            meas.wind_speed_100m = response_data['hourly']["windspeed_100m"][diff]
            meas.wind_gusts_10m = response_data['hourly']["windgusts_10m"][diff]
        j += 1
    return sites
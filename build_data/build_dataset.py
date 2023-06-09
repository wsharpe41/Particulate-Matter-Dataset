import requests
import pandas as pd

def get_elevation(sites):    
    print("Getting elevation data")
    locations = ""
    url = 'https://api.opentopodata.org/v1/aster30m'

    j = 0
    last_j = 0
    while j < len(sites):
        # Add the first site
        if j == 0:
            locations += f"{sites[j].lat},{sites[j].lon}"
        # Add the last site
        elif j == len(sites) - 1:
            locations += f"|{sites[j].lat},{sites[j].lon}"
        # Add the rest of the sites
        else:
            locations += f"|{sites[j].lat},{sites[j].lon}"
        
        if j % 99 == 0 and j > 0 or j == len(sites) - 1:
            print(f"Getting elevation data for sites {last_j} to {j}")
            params = {
                'locations': locations
            }
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error getting elevation data from opentopodata: {response.status_code}")
                print(f"Trying to find elevation with open-elevation API")
                url = 'https://api.open-elevation.com/api/v1/lookup'
                response = requests.get(url, params=params)
                if response.status_code != 200:
                    print(f"Error getting elevation data from open-elevation: {response.status_code}")
                    print(f"Error message: {response.text}")
                    print("Returning sites without elevation data")
                    return sites
            elevation = response.json()['results']
            # Add elevation to each site (CHECK THIS WORKS)
            for i in range(last_j, j):
                sites[i].elevation = elevation[i- last_j]['elevation']
            locations = ""
            last_j = j
        j += 1 

    return sites

def get_environmental_vars(sites: list) -> list:
    print("Getting environmental variables")
    # Add RH
    # Add wind speed
    #url = "https://archive-api.open-meteo.com/v1/archive"
    j = 0
    for site in sites:
        # Get first and last measurement dates as ISO6=8601 strings without timezone
        # Temp is in C, RH is in %, Rain is in mm, Wind speed is in m/s
        site_meas = site.measurements
        # Get the latest timestamp of measurements for this site
        last_meas = max([meas.timestamp for meas in site_meas])
        
        if len(site_meas) == 0:
            continue
        first_meas = str(site_meas[0].timestamp.isoformat().split("T")[0])
        last_meas = str(last_meas.isoformat().split("T")[0])
        
        # Get the first hour of the first measurement and the last hour of the last measurement
        first_hour = int(site_meas[0].timestamp.isoformat().split("T")[1].split(":")[0])
        
        # Take only 4 decimal places for lat and lon
        lat = format(f"{site.lat:.4f}")
        lon = format(f"{site.lon:.4f}")
        if site.elevation is None:
            site_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={first_meas}&end_date={last_meas}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,windspeed_100m,winddirection_10m,winddirection_100m,windgusts_10m,rain"
        else:
            site_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={first_meas}&end_date={last_meas}&elevation{site.elevation}&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,windspeed_100m,winddirection_10m,winddirection_100m,windgusts_10m,rain"
            
        response = requests.get(site_url)

        if response.status_code != 200:
            print(f"Error getting data: {response.status_code}")
            print(f"Error message: {response.text}")
            continue
        response_data = response.json()
        for meas in site_meas:
            if meas == site_meas[0] and j % 50 == 0:
                print(f"Getting environmental variables for site {j}")
            # Get the difference in hours between the first measurement and the current measurement
            diff = int((meas.timestamp - site_meas[0].timestamp).total_seconds() / 3600)
            # diff is the index of the measurement in the response_data (only works in meas is hourly)
            if diff <= len(response_data['hourly']["temperature_2m"]):
                meas.temp_2m = response_data['hourly']["temperature_2m"][diff+first_hour]
                meas.rh_2m = response_data['hourly']["relativehumidity_2m"][diff+first_hour]
                meas.rain = response_data['hourly']["rain"][diff+first_hour]
                meas.wind_dir_10m = response_data['hourly']["winddirection_10m"][diff+first_hour]
                meas.wind_dir_100m = response_data['hourly']["winddirection_100m"][diff+first_hour]
                meas.wind_speed_10m = response_data['hourly']["windspeed_10m"][diff+first_hour]
                meas.wind_speed_100m = response_data['hourly']["windspeed_100m"][diff+first_hour]
                meas.wind_gusts_10m = response_data['hourly']["windgusts_10m"][diff+first_hour]
        j += 1
    return sites
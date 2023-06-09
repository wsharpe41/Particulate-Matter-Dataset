import pandas as pd
import sqlalchemy as db

def populate_db(sites: list):
    # Connect to the database
    # Connect to the database
    print("Populating DB")
    engine = db.create_engine('sqlite:///pm_map.db')

    metadata = db.MetaData()
    metadata.reflect(engine)

    # Get the tables from the metadata
    measurements_table = metadata.tables['measurements']
    sites_table = metadata.tables['sites']

    # Read the sites and measurements from the database
    with engine.connect() as connection:
        sites_in_db = pd.read_sql_table("sites", connection)
        measurements_in_db = pd.read_sql_table("measurements", connection)

    # Filter out existing sites and measurements
    new_sites = []
    new_measurements = []

    for site in sites:
        #print(type(site.site_id))
        # Print if site.site_id is in sites_in_db["site_id"]
        #print((sites_in_db["site_id"] == int(site.site_id)).any())
        if (sites_in_db["site_id"] == int(site.site_id)).any():
            print("Site is already in the database")
            
        else:
            new_sites.append({
                "site_id": site.site_id,
                "latitude": site.lat,
                "longitude": site.lon,
                "elevation": site.elevation
            })

        for meas in site.measurements:
            #print((meas.timestamp))
            #print(measurements_in_db["timestamp"])
            if ((measurements_in_db["timestamp"] == meas.timestamp) & (measurements_in_db["site_id"] == int(site.site_id))).any():
                print("Measurement Already in DB")
                continue

            new_measurements.append({
                "timestamp": meas.timestamp,
                "pm": meas.value,
                "temperature": meas.temp_2m,
                "relative_humidity": meas.rh_2m,
                "rain": meas.rain,
                "wind_speed10": meas.wind_speed_10m,
                "wind_speed100": meas.wind_speed_100m,
                "wind_direction10": meas.wind_dir_10m,
                "wind_direction100": meas.wind_dir_100m,
                "wind_gusts10": meas.wind_gusts_10m,
                "site_id": site.site_id
            })

    # Insert data into tables
    with engine.begin() as connection:
        if new_sites:
            connection.execute(sites_table.insert(), new_sites)
        if new_measurements:
            connection.execute(measurements_table.insert(), new_measurements)

    print("Database populated")


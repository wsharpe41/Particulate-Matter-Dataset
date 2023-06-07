import pandas as pd
import sqlalchemy as db

def populate_db(sites: list):
    # Connect to the database
    engine = db.create_engine('sqlite:///pm_map.db')
    # Commented out since we won't be using it in this updated code
    # connection = engine.connect()

    metadata = db.MetaData()
    metadata.reflect(engine)

    # Get the tables from the database
    print(metadata.tables)
    measurements_table = metadata.tables['measurements']
    sites_table = metadata.tables['sites']

    # Define the measurements table with the bind parameter
    #measurements_table = db.Table('measurements', metadata, autoload=True, autoload_with=engine)

    # Define the sites table with the bind parameter
    #sites_table = db.Table('sites', metadata, autoload=True, autoload_with=engine)

    # Read the sites into the sites table
    sites_df = pd.DataFrame(columns=["site_id", "latitude", "longitude", "elevation"])
    measurements_df = pd.DataFrame(columns=["timestamp", "pm", "temperature", "relative_humidity", "rain", "wind_speed10", "wind_speed100", "wind_direction10", "wind_direction100",
                                            "wind_gusts10", "site_id"])
    
    # Add the sites and measurements to the respective DataFrames
    for site in sites:
        s_df = pd.DataFrame({"site_id": site.site_id, "latitude": site.lat, "longitude": site.lon, "elevation": site.elevation}, index=[0])
        sites_df = pd.concat([sites_df,s_df], ignore_index=True)
        for meas in site.measurements:
            meas_df  = pd.DataFrame({"timestamp": meas.timestamp, "pm": meas.value, "temperature": meas.temp_2m, "relative_humidity": meas.rh_2m, "rain": meas.rain,
                                                      "wind_speed10": meas.wind_speed_10m, "wind_speed100": meas.wind_speed_100m, "wind_direction10": meas.wind_dir_10m,
                                                      "wind_direction100": meas.wind_dir_100m, "wind_gusts10": meas.wind_gusts_10m, "site_id": site.site_id}, index=[0])
            measurements_df = pd.concat([measurements_df,meas_df], ignore_index=True)

    # Insert data into tables
    with engine.begin() as connection:
        connection.execute(sites_table.insert(), sites_df.to_dict(orient="records"))
        connection.execute(measurements_table.insert(), measurements_df.to_dict(orient="records"))

    print("Database populated")
    return

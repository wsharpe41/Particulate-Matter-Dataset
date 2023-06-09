# Take data from sqlite database, read it in and output it as a csv file
import sqlalchemy as db
import pandas as pd
PYDEVD_WARN_SLOW_RESOLVE_TIMEOUT = 10

engine = db.create_engine('sqlite:///pm_map.db')
metadata = db.MetaData()
metadata.reflect(engine)
with engine.connect() as connection:
    sites_in_db = pd.read_sql_table("sites", connection)
    measurements_in_db = pd.read_sql_table("measurements", connection)
    # Merge the two tables based on the site_id
    measurements_in_db = measurements_in_db.merge(sites_in_db, on="site_id")
    # Write the data to a csv file
    measurements_in_db.to_csv("data.csv")

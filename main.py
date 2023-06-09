import build_data.pyd_time_series as pyd_time_series
from build_data.pyd_time_series import set_measurement_time
import build_data.build_dataset as build_dataset
from create_db.populate_tables import populate_db
from create_db import create_tables
import time as time
import datetime

create_tables
db_time = datetime.datetime.now() - datetime.timedelta(days=6)

while db_time - datetime.datetime.now() < datetime.timedelta(days=365):
    start = time.time()
    set_measurement_time(db_time)
    
    sites = pyd_time_series.get_sites(750)
    sites = build_dataset.get_elevation(sites)
    sites = build_dataset.get_environmental_vars(sites)
    populate_db(sites)
    
    print(f"Time taken: {time.time() - start}")
    print(f"Data for {db_time} added to database")
    db_time = db_time - datetime.timedelta(days=10)
import build_data.pyd_time_series as pyd_time_series
import build_data.build_dataset as build_dataset
from create_db.populate_tables import populate_db
from create_db import create_tables
import time as time

start = time.time()
sites = pyd_time_series.get_sites()
sites = build_dataset.get_elevation(sites)
sites = build_dataset.get_environmental_vars(sites)
create_tables
populate_db(sites)
print(f"Time taken: {time.time() - start}")
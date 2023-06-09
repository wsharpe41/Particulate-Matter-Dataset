# Particulate-Matter-Dataset
This project provides a method to create a dataset for PM2.5 along with associated climate variables and upload that database to a SQL database (SQLite shown).

# Data
This makes use of the OpenAQ API (https://api.openaq.org), the Open Elevation api (https://api.open-elevation.com), and the Historical Weather API (https://open-meteo.com/en/docs/).
The OpenAQ API is used to get PM2.5 values, their associated time of measure, and longitudes and latitudes of various sensors and low-cost PM monitors.
This data is split in the database into "Site" objects which contain coordinates as well as elevations, and "Measurement" objects which contain values, times, and other climate variables for those times.
The Open Elevation API finds associated elevations with those sites. 
The Historical Weather API adds data on wind, rh, temperature, and rain to each measurement. These variables were chosen based on previously published work indicating these variables may be helpful in better predicting future PM values. This data is available with a 5 day lag.

## Dataset
A dataset with this information for ~9 months is available on Kaggle: https://www.kaggle.com/datasets/willsharpe/us-particulate-matter-with-climatic-variables-2023

## Current Setup
Currently the code shows a setup to collect the measurments from 100 sites in the US for a 10 day span in May 2023, with a max of 750 measurments per site. These values were chosen with some of the restrictions with the OpenAQ API in mind. I have seen request timeouts with my API calls when using less than 100 sites (408 response) and connection timeouts when trying to get more that 1000 measurements at once (504 response). The data range was chosen so that no one site would have more than 750 measurements in the time, and thus all data could be collected without worry.

# Usage
I have created one function for each API interface. They should be run in the order shown in main.py (get_sites, get_elevation, get_environmental_vars) as each call using information from the previous call. The create_tables script should only need to be called once, and would have to be modified if a database besides SQLite were desired. The populate_db function would also need to be slightly modified if a different SQL database were used. 

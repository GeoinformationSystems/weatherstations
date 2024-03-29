# weatherstations

A database deployment tool for static weather stations data and API access for [climatecharts](https://github.com/GeoinformationSystems/climatecharts). The project consists of two subprojects:
* api: An REST-API for access to the weatherstations data build on Java Servlet API.
* populate_db: A Django project to load and handle the weatherstations database

## /api

The project is build for a servlet engine like Tomcat.

Use the IDE of your choice (recommend Eclipse) to edit the files in the folder `/api`. To build the war file use on the command line `mvn clean install` or the IDEs capabilities. Copy the weatherstations-api.war from folder /api/target to the servlet engine of your choice.

### Usage

Call the url http://server_ip:server_port/weaterstations-api/ for a short overview of the capabilities of the servlet.
* `/getAllStations`: returns a JSON file with all available stations
* `/getStationData`: returns a JSON file with available temperature and precipitation data for a certain station within a given timer period. Use the follwing parameters:
	- `stationId`: on of the IDs from getAllStations
	- `minYear`: minimum year for the time period
	- `maxYear`: maximum year for the time period

## /populate_db

This project is build on Django with the following additional libraries: [haversine](https://pypi.org/project/haversine/), [psycopg2](http://initd.org/psycopg/docs/install.html), [pandas](https://pypi.org/project/pandas/), [numpy](https://pypi.org/project/numpy/), [sqlalchemy](https://pypi.org/project/sqlalchemy/).

### Prerequisite

For the correct usage a postgresql database with postgis installed and external datasets are necessary.

#### Python libraries

It is necessary to have the required python libraries installed on the system. Use the follwing command (or and equivalent for another system):

```bash
sudo pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r /populate_db/requirements.txt
```

#### Datasets

For the correct usage of `populate_db` it is required to have a default data structure with the latest datasets. We use the monthly average temperature and precipitation datasets from [Global Historical Climatology Network](https://www.ncdc.noaa.gov/ghcnm/). Please create the following folder structure in `/populate_db`:

```
data
+-- GHCN_monthly_prec
|   +-- ghcn-m_v4_prcp_inventory.txt
|   +-- v4_raw
|   |   +-- single CSV files
+-- GHCN_monthly_temp
|   +-- ghcnm.tavg.v4.0.1.latest.qcf.dat
|   +-- ghcnm.tavg.v4.0.1.latest.qcf.inv
+-- meta
|   +-- ghcnm-countries.txt
+-- qgis
```

Download the datasets from:
* `va_raw`: uncompress archive under [https://www.ncei.noaa.gov/data/ghcnm/v4beta/archive/](https://www.ncei.noaa.gov/data/ghcnm/v4beta/archive/)
* `ghcn-m_v4_prcp_inventory.txt`: [https://www.ncei.noaa.gov/data/ghcnm/v4beta/doc/ghcn-m_v4_prcp_inventory.txt](https://www.ncei.noaa.gov/data/ghcnm/v4beta/doc/ghcn-m_v4_prcp_inventory.txt)
* `ghcnm.tavg.v4.0.1.latest.qcf.dat` and `ghcnm.tavg.v4.0.1.latest.qcf.inv`: uncompress [https://www.ncei.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz](https://www.ncei.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcf.tar.gz) and **rename file name** -> replace date with "latest", eg. ghcnm.tavg.v4.0.1.20240205.qcf.inv =>ghcnm.tavg.v4.0.1.latest.qcf.inv
* `ghcnm-countries.txt`: [https://www.ncei.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt](https://www.ncei.noaa.gov/pub/data/ghcn/v4/ghcnm-countries.txt)


#### Database

The existence of a PostgreSQL database with PostgGIS installed is mandatory.
Create a database named `climatecharts_weatherstations` with PostGIS installed.

```bash
sudo -u postgres psql -c "CREATE DATABASE climatecharts_weatherstations"
sudo -u postgres psql -d climatecharts_weatherstations -c "CREATE EXTENSION postgis"
```

Connect Django to the database:

```bash
python populate_db/manage.py makemigrations
python populate_db/manage.py migrate
```

### Usage

The project provides different commands to handle the data. Use them with the following syntax (within the projects root folder):

```bash
python populate_db/manage.py <command> <option>
```

* `convert_data`: Converts precipitation beta 4 data into a suitable format.
* `export`: Export the climate database as csv file
* `load_data <option>`: Populates the database with initial data. Use the following options as `<option>`:
	- `A`: populate everything (stations -> temperature -> precipitation)
	- `S`: populate only stations (N.B: deletes temperature and precipitation data!)
	- `D`: (re)populate temperature and precipitation
* `statistics`: create statistics about the quality of the data in the climate database
* `update_stations`: update the climate database with statistically relevant data

For a newly created database it is recommended to run the `load_data A` command followed by the `update_stations` command.

To transfer the data from development database to production database use the following commands:

```bash
# on development machine
# use the option -format=custom for a compressed version
sudo -u postgres pg_dump --data-only --format=plain --table=populate_db_station --table=populate_db_stationdata --table=populate_db_stationduplicate climatecharts_weatherstations > uptodatedata.sql

# on production machine
sudo -u postgres psql -d climatecharts_weatherstations -f uptodatedata.sql
```

# License

The WeatherStations project is lincensed under the Apache License 2.0.

## Java Libraries

This project uses a collection of Java libraries:

* javax.servlet 4.0.1 - GPL2
* org.json 20220924 - JSON
* commons-io 2.11.0 - Apache 2.0
* org.apache.httpcomponents 4.5.13 - Apache 2.0
* com.sun.jersey 1.19 - GPL 1.1
* junit 4.13.1 - EPL 1.0
* org.postgresql 42.5.0 - BSD 2-clause
* javax.xml.bind 2.3.1 - CDDL 1.1

## Python Libraries

This project uses a collection of Python libraries:

* django - BSD license
* haversine - MIT license
* psycopg2 - LGPL license
* pandas - BSD license
* numpy - BSD license
* sqlalchemy - MIT license

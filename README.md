<div align="center">
<h1>CGC Grain Outcome Predictions</h1>

<br>

<h4>Ergot is a plant disease that infects the developing grains of cereals and grasses. When ergot bodies instead of kernels emerge during kernel formation, ergot symptoms become visible. To find a strategy to prevent it sooner, it is crucial to identify the factors that encourage it to grow in grain. Our project aims to build a tool that supports this research and provides tools for data analysis for the Canadian Grain Commission.<h4>


<br>
<br>
<div align="right">
<img src='.github/img/districtsAndLabels.png' width="500"/>
</div>
</div>

## Overview
- [Setting up the environment](#setting-up-the-environment)
    - [Host Dependencies](#host-dependencies)
    - [Setting up on Windows](#setting-up-on-windows)
    - [Setting up on Linux](#setting-up-on-linux)
    - [Containers](#containers)
        - [PGAdmin](#pgadmin)
        - [PostgreSQL](#postgresql)
        - [pgsync](#pgsync)
        - [Tensorflow](#tensorflow)
    - [Using Aviary Labs](#using-aviary-labs)
        - [Setting up credentials](#setting-up-credentials)
        - [Commands](#commands)
        - [Accessing the system with VSCode](#accessing-the-system-with-vscode)
- [Creating a model](#creating-a-model)
- [Data Sources](#data-sources)
- [Database Tables](#database-tables)
    - Final tables
        - [agg_ergot_sample](#agg_ergot_sample)
        - [agg_ergot_sample_v2](#agg_ergot_sample_v2)
        - [ergot_sample_feat_eng](#ergot_sample_feat_eng)
        - [dataset_daily_sat](#dataset_daily_sat)
        - [dataset_weekly_sat](#dataset_weekly_sat)
        - [dataset_monthly_sat](#dataset_monthly_sat)
        - [dataset_cross_monthly_sat](#dataset_cross_monthly_sat)
        - [dataset_cross_weekly_sat_JFMA](#dataset_cross_weekly_sat_JFMA)
        - [dataset_cross_weekly_sat_MAMJ](#dataset_cross_weekly_sat_MAMJ)
        - [dataset_cross_weekly_sat_MJJA](#dataset_cross_weekly_sat_MJJA)
        - [dataset_cross_weekly_sat_JASO](#dataset_cross_weekly_sat_JASO)
        - [dataset_daily_station](#dataset_daily_station)
        - [dataset_weekly_station](#dataset_weekly_station)
        - [dataset_monthly_station](#dataset_monthly_station)
        - [dataset_cross_monthly_station](#dataset_cross_monthly_station)
        - [dataset_cross_weekly_station_JFMA](#dataset_cross_weekly_station_JFMA)
        - [dataset_cross_weekly_station_MAMJ](#dataset_cross_weekly_station_MAMJ)
        - [dataset_cross_weekly_station_MJJA](#dataset_cross_weekly_station_MJJA)
        - [dataset_cross_weekly_station_JASO](#dataset_cross_weekly_station_JASO)
        - [dataset_daily_sat_soil](#dataset_daily_sat_soil)
        - [dataset_weekly_sat_soil](#dataset_weekly_sat_soil)
        - [dataset_monthly_sat_soil](#dataset_monthly_sat_soil)
        - [dataset_daily_station_soil](#dataset_daily_station_soil)
        - [dataset_weekly_station_soil](#dataset_weekly_station_soil)
        - [dataset_monthly_station_soil](#dataset_monthly_station_soil)
    - Copernicus
        - [copernicus_satelite_data](#copernicus_satelite_data)
        - [agg_day_copernicus_satellite_data](#agg_day_copernicus_satellite_data)
    - Ergot
        - [ergot_sample](#ergot_sample)
    - Geography
        - [census_ag_regions](#census_ag_regions)
    - Soil
        - [labeled_soil](#labeled_soil)
        - [soil_components](#soil_components)
        - [soil_data](#soil_data)
        - [soil_geometry](#soil_geometry)
        - [soil_surronding_land](#soil_surronding_land)
        - [agg_soil_data](#agg_soil_data)
    - Soil Moisture
        - [soil_moisture](#soil_moisture)
        - [agg_soil_moisture](#agg_soil_moisture)
    - Weather Station Data
        - [ab_dly_station_data](#ab_dly_station_data)
        - [mb_dly_staion_data](#mb_dly_staion_data)
        - [sk_dly_station_data](#sk_dly_station_data)
        - [ab_hly_station_data](#ab_hly_station_data)
        - [mb_hly_station_data](#mb_hly_station_data)
        - [sk_hly_station_data](sk_hly_station_data)
        - [agg_weather_combined](#agg_weather_combined)
    - Weather Station Metadata
        - [stations_dly](#stations_dly)
        - [stations_hly](#stations_hly)
        - [station_data_last_updated](#station_data_last_updated)
- [Useful links](#useful-links)

<br>
<hr>
<br>

## Setting up the environment
Our current environment uses docker compose to launch containers housing [PGADMIN4](#pgadmin), [PostgreSQL](#postgresql) and the latest [Tensorflow Container with Jupyter Lab](#tensorflow). 



### Host Dependencies
- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/)
- [Tensorflow](https://www.tensorflow.org/install/docker)
    - NVIDIA GPU Drivers (if using tensorflow-gpu) follow [official guide](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/running.html) guide for installation.

<br>

### Setting up on Windows
1. Install dependencies and clone project

2. Navigate to the project directory 

3. Create a .env file which satisfies the requirements of [.env.template](src/docker/.env.template). **Ensure this .env file can be found inside of the src/docker directory**

4. Run ```setup.bat``` located in the root folder of the project directory. This launches 3 different containers: postgres, pgadmin, and tensorflow-cpu

5. Refresh the webpages that appear to respectively load pgadmin and Jupyter labs. Jupyter labs requires a token for entry.

[back to top](#overview)
<br>

### Setting up on Linux
1. Install dependencies and clone project. Note that installation commands should be ran with BASH. BASH can be activated by ```bash```

1. Navigate to the project directory then enter the command ```cd src/docker```

2. Create a .env file which satisfies the requirements of [.env.template](src/docker/.env.template)

3. Run docker-compose for the containers you would like to use from the src/docker directory. The following is a list of the docker compose options:
    - all containers: ```sudo docker-compose --env-file=.env -f gpu-swarm.yaml up -d```
    - postgres: ```sudo docker-compose --env-file=.env -f postgres.yaml up -d```
    - pgadmin: ```sudo docker-compose --env-file=.env -f pgadmin.yaml up -d```
    - tensorflow-gpu: ```sudo docker-compose -f tensorflow-gpu.yaml up -d```
    - tensorflow-cpu: ```sudo docker-compose -f tensorflow-cpu.yaml up -d```

[back to top](#overview)
<br>

### Containers 

#### PGADMIN
- PGADMIN (optional) is a web-based interface for managing PostgreSQL databases. It is used to manage the database and can be accessed at http://localhost:5433. The default credentials are:
    - Email: xxxxxxxx
    - Password: xxxx

#### PostgreSQL
- PostgreSQL is a relational database management system. It is used to store the data and can be accessed at http://localhost:5432. The default credentials are:
    - Username: xxxxxxxx
    - Password: xxxx

#### pgsync
- pgsync is used to synchroniza postgres databases
- ```sudo apt-get install ruby-dev libpq-dev build-essential```
- ```docker pull ankane/pgsync```
- ```alias pgsync="docker run -ti ankane/pgsync"```

#### Tensorflow
- Tensorflow-gpu is a machine learning framework. It is used to train the model and can be accessed at http://localhost:8888. 

**NOTE: Jupyter Labs requires a token for entry. This token can be located in the following ways:**
- (*windows*) printed in the terminal used to run setup.bat 
- (*windows*) printed in the terminal of the docker container
- (*windows*) ```docker logs [container name]``` 
- (*linux*) ```sudo docker logs [container name]``` 

[back to top](#overview)
<br>
<hr>
<br>

## Using Aviary Labs
### Available machines:
- woodswallow-01
- woodswallow-02
- woodswallow-03
- woodswallow-04 (**holds main database**)
- guan (**holds test database**)

<br>

### Setting up credentials:
1. [Generate a personal access token for your GitHub account](https://github.com/settings/developers)
2. Run the following commands and use the token generated in step 1 as the password  
```git config --global user.name "yourusername"```  
```git config --global user.email "yourusername@users.noreply.github.com"```  
```git config --global user.password "your password"```  

**Note**: login information may differ if using a private email address  
These can later be verified by running
```git config --list```

[back to top](#overview)
<br>

### Commands
#### Cloning

```git clone https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions.git```

#### Connecting via SSH

```ssh UMNetID@machine.cs.umanitoba.ca```  

#### Connecting via tunnel

```ssh UMnetID@machine.cs.umanitoba.ca -NL yourLocalPort:localhost:machinePort``` 

<br>

### Accessing the system with VSCode
1. Install Remote - SSH extension
2. In the bottom left corner click on open a remote window
3. Click to connect to host
4. Enter aviary information in and follow prompts
5. Click on SSH: machine etc... (once connected - same place as in step 2)
6. Click attach to a running container
7. Select the desired container and follow prompts
8. Default location is root access .. and then select data folder

[back to top](#overview)
<br>
<hr>
<br>

## Creating a model

### 1. Extract, Transform, Load
- Gathering data
- Aggregation
- Visualization
- Feature engineering

**NOTE**: Gathering and aggregating data can easily be done using the [loadData notebook](https://github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions/blob/main/src/loadData.ipynb) 


### 2. Dataset Selection
- Choosing which feature to predict
- Ensuring data similar to what you are attempting to predict is removed

### 3. Dataset Splitting
- Creating training and testing sets, some ways to do this include:
    - 80/20 train/test split
    - Assigning entire years of data to a train/test split

### 4. Dataset Balancing
- Upsampling: underrepresented attribute in an unbalanced dataset **gets copied and paired** with multiple splits of the overrepresented attribute  
- Downsampling: overrepresented attribute in an unbalanced dataset has some of its isntances removed  
- Combination method SMOTEENN: **creates new instances** of the underrepresented attribute by using the k nearest neighbours of the existing instances, then **removes instances** of the overrepresented attribute  

### 5. Categorical Encoding
- Specifying categorical columns for one hot encoding (**possible class values are turned into boolean features**)

### 6. Model selection
- Pick a model 
- Hyperparameter (or hyperparameter range) tuning
- Cross validation
- Evaluation metrics
    - Accuracy
    - Precision
    - Recall
    - F1 score
    - Confusion matrix
    - ROC curve
    - AUC score
- Feature importance/selection

### 7. Regularization/Normalization
Data is adjusted in order to meet model requirements or as an attempt to improve overall performance. This can include the following:
- Imputation (replacing undesired values with mean, median, 0 etc...)
- Scaling
    - Standard scaler: **much less affected by outliers**
    - Min max scaler: **consistant range of values accross features (desirable)**
- Transforming a distribution into a bell curve (desirable, models expect this)
    - log
    - square root
    - cube root



### 8. Run
- Training the model with the train set
- Evaluation with the test set
- Using the output model to make further predictions

[back to top](#overview)
<br>
<hr>
<br>

## Data Sources

<br>

- [2006 Census Agricultural Regions](https://www150.statcan.gc.ca/n1/pub/92-174-x/2007000/carboundary/gcar000b07a_e.zip): digital boundaries for Canada's agriculture regions 
- [Weather Stations](https://dd.weather.gc.ca/climate/observations/climate_station_list.csv): list of weather stations that collect weather data spread throughout Canada
- [Harvest Canada Ergot Data](https://www.grainscanada.gc.ca/en/grain-quality/harvest-sample/): grain samples tested for Ergot
- [Soil Data](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/index.html): multiple data sources containing Canadian Soil data
- [Soil Moisture Data](https://www.esa.int/Applications/Observing_the_Earth/Space_for_our_climate/Nearly_four_decades_of_soil_moisture_data_now_available): satellite moisture data
    - **NOTE** Files can be downloaded via SFTP, however, permission must be granted and requests are time sensitive
- [Hourly Weather Station Data](https://dd.weather.gc.ca/climate/observations/hourly/): weather data (hourly) collected by Canadian weather stations
- [Daily Weather Station Data](https://dd.weather.gc.ca/climate/observations/daily/): weather data (daily) collected by Canadian weather stations
- [ERA5-Land Satelite Data](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview): satelite weather data 
    - **NOTE** Copernicus needs an API key which if access has been/still is granted can be setup with the [following steps](https://cds.climate.copernicus.eu/api-how-to)

<br>

[back to top](#overview)
<br>
<hr>
<br>

## Database Tables
![Database schema](.github/img/tables.png)

### Final Tables

### dataset_daily_sat
- Schema: public
- Columns: 59

A table containing daily aggregate weather data from the copernicus satellite dataset.
<details><summary>Vertical view dataset_daily_sat attribute list</summary>

|Attribute                          | Type              | Unit  | Description | Constraints |
|-----------------------------------|-------------------|-------|-------------|-------------|
|year                               | bigint            |       |             |             |
|month                              | bigint            |       |             |             |
|day                                | bigint            |       |             |             |
|cr_num                             | bigint            |       |             |             |
|district                           | bigint            |       |             |             |
|min_dewpoint_temperature           | double precision  | °C    |             |             |
|max_dewpoint_temperature           | double precision  | °C    |             |             |
|mean_dewpoint_temperature          | double precision  | °C    |             |             |
|min_temperature                    | double precision  | °C    |             |             |
|max_temperature                    | double precision  | °C    |             |             |
|mean_temperature                   | double precision  | °C    |             |             |
|min_evaporation_from_bare_soil     | double precision  | mm    |             |             |
|max_evaporation_from_bare_soil     | double precision  | mm    |             |             |
|mean_evaporation_from_bare_soil    | double precision  | mm    |             |             |
|min_skin_reservoir_content         | double precision  | mm    |             |             |
|max_skin_reservoir_content         | double precision  | mm    |             |             |
|mean_skin_reservoir_content        | double precision  | mm    |             |             |
|min_skin_temperature               | double precision  | °C    |             |             |
|max_skin_temperature               | double precision  | °C    |             |             |
|mean_skin_temperature              | double precision  | °C    |             |             |
|min_snowmelt                       | double precision  | mm    |             |             |
|max_snowmelt                       | double precision  | mm    |             |             |
|mean_snowmelt                      | double precision  | mm    |             |             |
|min_soil_temperature_level_1       | double precision  | °C    |             |             |
|max_soil_temperature_level_1       | double precision  | °C    |             |             |
|mean_soil_temperature_level_1      | double precision  | °C    |             |             |
|min_soil_temperature_level_2       | double precision  | °C    |             |             |
|max_soil_temperature_level_2       | double precision  | °C    |             |             |
|mean_soil_temperature_level_2      | double precision  | °C    |             |             |
|min_soil_temperature_level_3       | double precision  | °C    |             |             |
|max_soil_temperature_level_3       | double precision  | °C    |             |             |
|mean_soil_temperature_level_3      | double precision  | °C    |             |             |
|min_soil_temperature_level_4       | double precision  | °C    |             |             |
|max_soil_temperature_level_4       | double precision  | °C    |             |             |
|mean_soil_temperature_level_4      | double precision  | °C    |             |             |
|min_surface_net_solar_radiation    | double precision  | W/m²  |             |             |
|max_surface_net_solar_radiation    | double precision  | W/m²  |             |             |
|mean_surface_net_solar_radiation   | double precision  | W/m²  |             |             |
|min_surface_pressure               | double precision  | hPa   |             |             |
|max_surface_pressure               | double precision  | hPa   |             |             |
|mean_surface_pressure              | double precision  | hPa   |             |             |
|min_volumetric_soil_water_layer_1  | double precision  | m³/m³ |             |             |
|max_volumetric_soil_water_layer_1  | double precision  | m³/m³ |             |             |
|mean_volumetric_soil_water_layer_1 | double precision  | m³/m³ |             |             |
|min_volumetric_soil_water_layer_2  | double precision  | m³/m³ |             |             |
|max_volumetric_soil_water_layer_2  | double precision  | m³/m³ |             |             |
|mean_volumetric_soil_water_layer_2 | double precision  | m³/m³ |             |             |
|min_volumetric_soil_water_layer_3  | double precision  | m³/m³ |             |             |
|max_volumetric_soil_water_layer_3  | double precision  | m³/m³ |             |             |
|mean_volumetric_soil_water_layer_3 | double precision  | m³/m³ |             |             |
|min_volumetric_soil_water_layer_4  | double precision  | m³/m³ |             |             |
|max_volumetric_soil_water_layer_4  | double precision  | m³/m³ |             |             |
|mean_volumetric_soil_water_layer_4 | double precision  | m³/m³ |             |             |
|min_leaf_area_index_high_vegetation| double precision  |       |             |             |
|max_leaf_area_index_high_vegetation| double precision  |       |             |             |
|mean_leaf_area_index_high_vegetation|double precision  |       |             |             |
|min_leaf_area_index_low_vegetation | double precision  |       |             |             |
|max_leaf_area_index_low_vegetation | double precision  |       |             |             |
|mean_leaf_area_index_low_vegetation| double precision  |       |             |             |

</details>

[back to top](#overview)
<br>
<br>

### dataset_weekly_sat
- Schema: public
- Columns: 58

A table containing weekly aggregate weather data from the copernicus satellite dataset.
<details><summary>Vertical view dataset_weekly_sat attribute list</summary>

| Attribute                           | Type             | Unit | Description | Constraint |
|-------------------------------------|------------------|------|-------------|------------|
| year                                | bigint           |      |             |            |
| month                               | bigint           |      |             |            |
| week_of_year                        | bigint           |      |             |            |
| district                            | bigint           |      |             |            |
| min_dewpoint_temperature            | double precision | °C   |             |            |
| min_temperature                     | double precision | °C   |             |            |
| min_evaporation_from_bare_soil      | double precision | mm   |             |            |
| min_skin_reservoir_content          | double precision | mm   |             |            |
| min_skin_temperature                | double precision | °C   |             |            |
| min_snowmelt                        | double precision | mm   |             |            |
| min_soil_temperature_level_1        | double precision | °C   |             |            |
| min_soil_temperature_level_2        | double precision | °C   |             |            |
| min_soil_temperature_level_3        | double precision | °C   |             |            |
| min_soil_temperature_level_4        | double precision | °C   |             |            |
| min_surface_net_solar_radiation     | double precision | W/m² |             |            |
| min_surface_pressure                | double precision | hPa  |             |            |
| min_volumetric_soil_water_layer_1   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_2   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_3   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_4   | double precision | m³/m³|             |            |
| min_leaf_area_index_high_vegetation | double precision |      |             |            |
| min_leaf_area_index_low_vegetation  | double precision |      |             |            |
| max_dewpoint_temperature            | double precision | °C   |             |            |
| max_temperature                     | double precision | °C   |             |            |
| max_evaporation_from_bare_soil      | double precision | mm   |             |            |
| max_skin_reservoir_content          | double precision | mm   |             |            |
| max_skin_temperature                | double precision | °C   |             |            |
| max_snowmelt                        | double precision | mm   |             |            |
| max_soil_temperature_level_1        | double precision | °C   |             |            |
| max_soil_temperature_level_2        | double precision | °C   |             |            |
| max_soil_temperature_level_3        | double precision | °C   |             |            |
| max_soil_temperature_level_4        | double precision | °C   |             |            |
| max_surface_net_solar_radiation     | double precision | W/m² |             |            |
| max_surface_pressure                | double precision | hPa  |             |            |
| max_volumetric_soil_water_layer_1   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_2   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_3   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_4   | double precision | m³/m³|             |            |
| max_leaf_area_index_high_vegetation | double precision |      |             |            |
| max_leaf_area_index_low_vegetation  | double precision |      |             |            |
| mean_dewpoint_temperature           | double precision | °C   |             |            |
| mean_temperature                    | double precision | °C   |             |            |
| mean_evaporation_from_bare_soil     | double precision | mm   |             |            |
| mean_skin_reservoir_content         | double precision | mm   |             |            |
| mean_skin_temperature               | double precision | °C   |             |            |
| mean_snowmelt                       | double precision | mm   |             |            |
| mean_soil_temperature_level_1       | double precision | °C   |             |            |
| mean_soil_temperature_level_2       | double precision | °C   |             |            |
| mean_soil_temperature_level_3       | double precision | °C   |             |            |
| mean_soil_temperature_level_4       | double precision | °C   |             |            |
| mean_surface_net_solar_radiation    | double precision | W/m² |             |            |
| mean_surface_pressure               | double precision | hPa  |             |            |
| mean_volumetric_soil_water_layer_1  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_2  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_3  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_4  | double precision | m³/m³|             |            |
| mean_leaf_area_index_high_vegetation| double precision |      |             |            |
| mean_leaf_area_index_low_vegetation | double precision |      |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_monthly_sat
- Schema: public
- Columns: 57

A table containing monthly aggregate weather data from the copernicus satellite dataset.
<details><summary>Vertical view dataset_monthly_sat attribute list</summary>

| Attribute                           | Type             | Unit | Description | Constraint |
|-------------------------------------|------------------|------|-------------|------------|
| year                                | bigint           |      |             |            |
| month                               | bigint           |      |             |            |
| district                            | bigint           |      |             |            |
| min_dewpoint_temperature            | double precision | °C   |             |            |
| min_temperature                     | double precision | °C   |             |            |
| min_evaporation_from_bare_soil      | double precision | mm   |             |            |
| min_skin_reservoir_content          | double precision | mm   |             |            |
| min_skin_temperature                | double precision | °C   |             |            |
| min_snowmelt                        | double precision | mm   |             |            |
| min_soil_temperature_level_1        | double precision | °C   |             |            |
| min_soil_temperature_level_2        | double precision | °C   |             |            |
| min_soil_temperature_level_3        | double precision | °C   |             |            |
| min_soil_temperature_level_4        | double precision | °C   |             |            |
| min_surface_net_solar_radiation     | double precision | W/m² |             |            |
| min_surface_pressure                | double precision | hPa  |             |            |
| min_volumetric_soil_water_layer_1   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_2   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_3   | double precision | m³/m³|             |            |
| min_volumetric_soil_water_layer_4   | double precision | m³/m³|             |            |
| min_leaf_area_index_high_vegetation | double precision |      |             |            |
| min_leaf_area_index_low_vegetation  | double precision |      |             |            |
| max_dewpoint_temperature            | double precision | °C   |             |            |
| max_temperature                     | double precision | °C   |             |            |
| max_evaporation_from_bare_soil      | double precision | mm   |             |            |
| max_skin_reservoir_content          | double precision | mm   |             |            |
| max_skin_temperature                | double precision | °C   |             |            |
| max_snowmelt                        | double precision | mm   |             |            |
| max_soil_temperature_level_1        | double precision | °C   |             |            |
| max_soil_temperature_level_2        | double precision | °C   |             |            |
| max_soil_temperature_level_3        | double precision | °C   |             |            |
| max_soil_temperature_level_4        | double precision | °C   |             |            |
| max_surface_net_solar_radiation     | double precision | W/m² |             |            |
| max_surface_pressure                | double precision | hPa  |             |            |
| max_volumetric_soil_water_layer_1   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_2   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_3   | double precision | m³/m³|             |            |
| max_volumetric_soil_water_layer_4   | double precision | m³/m³|             |            |
| max_leaf_area_index_high_vegetation | double precision |      |             |            |
| max_leaf_area_index_low_vegetation  | double precision |      |             |            |
| mean_dewpoint_temperature           | double precision | °C   |             |            |
| mean_temperature                    | double precision | °C   |             |            |
| mean_evaporation_from_bare_soil     | double precision | mm   |             |            |
| mean_skin_reservoir_content         | double precision | mm   |             |            |
| mean_skin_temperature               | double precision | °C   |             |            |
| mean_snowmelt                       | double precision | mm   |             |            |
| mean_soil_temperature_level_1       | double precision | °C   |             |            |
| mean_soil_temperature_level_2       | double precision | °C   |             |            |
| mean_soil_temperature_level_3       | double precision | °C   |             |            |
| mean_soil_temperature_level_4       | double precision | °C   |             |            |
| mean_surface_net_solar_radiation    | double precision | W/m² |             |            |
| mean_surface_pressure               | double precision | hPa  |             |            |
| mean_volumetric_soil_water_layer_1  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_2  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_3  | double precision | m³/m³|             |            |
| mean_volumetric_soil_water_layer_4  | double precision | m³/m³|             |            |
| mean_leaf_area_index_high_vegetation| double precision |      |             |            |
| mean_leaf_area_index_low_vegetation | double precision |      |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_monthly_sat
- Schema: public
- Columns: 650

A table containing monthly aggregate weather data from the copernicus satellite dataset. The data is crossed by the month to help determine the importance of each parameter of each month is to the model.
<details><summary>Vertical view dataset_cross_monthly_sat attribute list</summary>

| Attribute                           | Type             | Unit | Description | Constraint |
|-------------------------------------|------------------|------|-------------|------------|
| year                                | bigint           |      |             |            |
| district                            | bigint           |      |             |            |
| 1:min_dewpoint_temperature          | double precision |      |             |            |
| 1:min_temperature                   | double precision |      |             |            |
| 1:min_evaporation_from_bare_soil    | double precision |      |             |            |
| 1:min_skin_reservoir_content        | double precision |      |             |            |
| 1:min_skin_temperature              | double precision |      |             |            |
| 1:min_snowmelt                      | double precision |      |             |            |
| 1:min_soil_temperature_level_1      | double precision |      |             |            |
| 1:min_soil_temperature_level_2      | double precision |      |             |            |
| 1:min_soil_temperature_level_3      | double precision |      |             |            |
| 1:min_soil_temperature_level_4      | double precision |      |             |            |
| 1:min_surface_net_solar_radiation   | double precision |      |             |            |
| 1:min_surface_pressure              | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 1:min_leaf_area_index_high_vegetation| double precision |     |             |            |
| 1:min_leaf_area_index_low_vegetation | double precision |     |             |            |
| 1:max_dewpoint_temperature          | double precision |      |             |            |
| 1:max_temperature                   | double precision |      |             |            |
| 1:max_evaporation_from_bare_soil    | double precision |      |             |            |
| 1:max_skin_reservoir_content        | double precision |      |             |            |
| 1:max_skin_temperature              | double precision |      |             |            |
| 1:max_snowmelt                      | double precision |      |             |            |
| 1:max_soil_temperature_level_1      | double precision |      |             |            |
| 1:max_soil_temperature_level_2      | double precision |      |             |            |
| 1:max_soil_temperature_level_3      | double precision |      |             |            |
| 1:max_soil_temperature_level_4      | double precision |      |             |            |
| 1:max_surface_net_solar_radiation   | double precision |      |             |            |
| 1:max_surface_pressure              | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 1:max_leaf_area_index_high_vegetation| double precision |     |             |            |
| 1:max_leaf_area_index_low_vegetation | double precision |     |             |            |
| 1:mean_dewpoint_temperature         | double precision |      |             |            |
| 1:mean_temperature                  | double precision |      |             |            |
| 1:mean_evaporation_from_bare_soil   | double precision |      |             |            |
| 1:mean_skin_reservoir_content       | double precision |      |             |            |
| 1:mean_skin_temperature             | double precision |      |             |            |
| 1:mean_snowmelt                     | double precision |      |             |            |
| 1:mean_soil_temperature_level_1     | double precision |      |             |            |
| 1:mean_soil_temperature_level_2     | double precision |      |             |            |
| 1:mean_soil_temperature_level_3     | double precision |      |             |            |
| 1:mean_soil_temperature_level_4     | double precision |      |             |            |
| 1:mean_surface_net_solar_radiation  | double precision |      |             |            |
| 1:mean_surface_pressure             | double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_1| double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_2| double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_3| double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_4| double precision |      |             |            |
| 1:mean_leaf_area_index_high_vegetation| double precision |     |             |            |
| 1:mean_leaf_area_index_low_vegetation | double precision |     |             |            |
| ...                           | ...             | ... | ... | ... |
| 12:min_dewpoint_temperature          | double precision |      |             |            |
| 12:min_temperature                   | double precision |      |             |            |
| 12:min_evaporation_from_bare_soil    | double precision |      |             |            |
| 12:min_skin_reservoir_content        | double precision |      |             |            |
| 12:min_skin_temperature              | double precision |      |             |            |
| 12:min_snowmelt                      | double precision |      |             |            |
| 12:min_soil_temperature_level_1      | double precision |      |             |            |
| 12:min_soil_temperature_level_2      | double precision |      |             |            |
| 12:min_soil_temperature_level_3      | double precision |      |             |            |
| 12:min_soil_temperature_level_4      | double precision |      |             |            |
| 12:min_surface_net_solar_radiation   | double precision |      |             |            |
| 12:min_surface_pressure              | double precision |      |             |            |
| 12:min_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 12:min_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 12:min_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 12:min_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 12:min_leaf_area_index_high_vegetation| double precision |     |             |            |
| 12:min_leaf_area_index_low_vegetation | double precision |     |             |            |
| 12:max_dewpoint_temperature          | double precision |      |             |            |
| 12:max_temperature                   | double precision |      |             |            |
| 12:max_evaporation_from_bare_soil    | double precision |      |             |            |
| 12:max_skin_reservoir_content        | double precision |      |             |            |
| 12:max_skin_temperature              | double precision |      |             |            |
| 12:max_snowmelt                      | double precision |      |             |            |
| 12:max_soil_temperature_level_1      | double precision |      |             |            |
| 12:max_soil_temperature_level_2      | double precision |      |             |            |
| 12:max_soil_temperature_level_3      | double precision |      |             |            |
| 12:max_soil_temperature_level_4      | double precision |      |             |            |
| 12:max_surface_net_solar_radiation   | double precision |      |             |            |
| 12:max_surface_pressure              | double precision |      |             |            |
| 12:max_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 12:max_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 12:max_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 12:max_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 12:max_leaf_area_index_high_vegetation| double precision |     |             |            |
| 12:max_leaf_area_index_low_vegetation | double precision |     |             |            |
| 12:mean_dewpoint_temperature         | double precision |      |             |            |
| 12:mean_temperature                  | double precision |      |             |            |
| 12:mean_evaporation_from_bare_soil   | double precision |      |             |            |
| 12:mean_skin_reservoir_content       | double precision |      |             |            |
| 12:mean_skin_temperature             | double precision |      |             |            |
| 12:mean_snowmelt                     | double precision |      |             |            |
| 12:mean_soil_temperature_level_1     | double precision |      |             |            |
| 12:mean_soil_temperature_level_2     | double precision |      |             |            |
| 12:mean_soil_temperature_level_3     | double precision |      |             |            |
| 12:mean_soil_temperature_level_4     | double precision |      |             |            |
| 12:mean_surface_net_solar_radiation  | double precision |      |             |            |
| 12:mean_surface_pressure             | double precision |      |             |            |
| 12:mean_volumetric_soil_water_layer_1| double precision |      |             |            |
| 12:mean_volumetric_soil_water_layer_2| double precision |      |             |            |
| 12:mean_volumetric_soil_water_layer_3| double precision |      |             |            |
| 12:mean_volumetric_soil_water_layer_4| double precision |      |             |            |
| 12:mean_leaf_area_index_high_vegetation| double precision |     |             |            |
| 12:mean_leaf_area_index_low_vegetation | double precision |     |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_sat_JFMA
- Schema: public
- Columns: 866

A table containing weekly aggregate weather data from the copernicus satellite dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of January, February, March, and April.
<details><summary>Vertical view dataset_cross_weekly_sat_JFMA attribute list</summary>

| Attribute                             | Type             | Unit | Description | Constraint |
|---------------------------------------|------------------|------|-------------|------------|
| year                                  | bigint           |      |             |            |
| district                              | bigint           |      |             |            |
| 1:min_dewpoint_temperature           | double precision |      |             |            |
| 1:min_temperature                    | double precision |      |             |            |
| 1:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 1:min_skin_reservoir_content         | double precision |      |             |            |
| 1:min_skin_temperature               | double precision |      |             |            |
| 1:min_snowmelt                       | double precision |      |             |            |
| 1:min_soil_temperature_level_1       | double precision |      |             |            |
| 1:min_soil_temperature_level_2       | double precision |      |             |            |
| 1:min_soil_temperature_level_3       | double precision |      |             |            |
| 1:min_soil_temperature_level_4       | double precision |      |             |            |
| 1:min_surface_net_solar_radiation    | double precision |      |             |            |
| 1:min_surface_pressure               | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 1:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 1:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 1:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 1:max_dewpoint_temperature           | double precision |      |             |            |
| 1:max_temperature                    | double precision |      |             |            |
| 1:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 1:max_skin_reservoir_content         | double precision |      |             |            |
| 1:max_skin_temperature               | double precision |      |             |            |
| 1:max_snowmelt                       | double precision |      |             |            |
| 1:max_soil_temperature_level_1       | double precision |      |             |            |
| 1:max_soil_temperature_level_2       | double precision |      |             |            |
| 1:max_soil_temperature_level_3       | double precision |      |             |            |
| 1:max_soil_temperature_level_4       | double precision |      |             |            |
| 1:max_surface_net_solar_radiation    | double precision |      |             |            |
| 1:max_surface_pressure               | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 1:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 1:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 1:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 1:mean_dewpoint_temperature          | double precision |      |             |            |
| 1:mean_temperature                   | double precision |      |             |            |
| 1:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 1:mean_skin_reservoir_content        | double precision |      |             |            |
| 1:mean_skin_temperature              | double precision |      |             |            |
| 1:mean_snowmelt                      | double precision |      |             |            |
| 1:mean_soil_temperature_level_1      | double precision |      |             |            |
| 1:mean_soil_temperature_level_2      | double precision |      |             |            |
| 1:mean_soil_temperature_level_3      | double precision |      |             |            |
| 1:mean_soil_temperature_level_4      | double precision |      |             |            |
| 1:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 1:mean_surface_pressure              | double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 1:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 1:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 1:mean_leaf_area_index_low_vegetation | double precision|      |             |            |
| ...                             | ...             | ... | ... | ... |
| 16:min_dewpoint_temperature           | double precision |      |             |            |
| 16:min_temperature                    | double precision |      |             |            |
| 16:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 16:min_skin_reservoir_content         | double precision |      |             |            |
| 16:min_skin_temperature               | double precision |      |             |            |
| 16:min_snowmelt                       | double precision |      |             |            |
| 16:min_soil_temperature_level_1       | double precision |      |             |            |
| 16:min_soil_temperature_level_2       | double precision |      |             |            |
| 16:min_soil_temperature_level_3       | double precision |      |             |            |
| 16:min_soil_temperature_level_4       | double precision |      |             |            |
| 16:min_surface_net_solar_radiation    | double precision |      |             |            |
| 16:min_surface_pressure               | double precision |      |             |            |
| 16:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 16:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 16:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 16:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 16:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 16:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 16:max_dewpoint_temperature           | double precision |      |             |            |
| 16:max_temperature                    | double precision |      |             |            |
| 16:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 16:max_skin_reservoir_content         | double precision |      |             |            |
| 16:max_skin_temperature               | double precision |      |             |            |
| 16:max_snowmelt                       | double precision |      |             |            |
| 16:max_soil_temperature_level_1       | double precision |      |             |            |
| 16:max_soil_temperature_level_2       | double precision |      |             |            |
| 16:max_soil_temperature_level_3       | double precision |      |             |            |
| 16:max_soil_temperature_level_4       | double precision |      |             |            |
| 16:max_surface_net_solar_radiation    | double precision |      |             |            |
| 16:max_surface_pressure               | double precision |      |             |            |
| 16:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 16:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 16:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 16:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 16:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 16:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 16:mean_dewpoint_temperature          | double precision |      |             |            |
| 16:mean_temperature                   | double precision |      |             |            |
| 16:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 16:mean_skin_reservoir_content        | double precision |      |             |            |
| 16:mean_skin_temperature              | double precision |      |             |            |
| 16:mean_snowmelt                      | double precision |      |             |            |
| 16:mean_soil_temperature_level_1      | double precision |      |             |            |
| 16:mean_soil_temperature_level_2      | double precision |      |             |            |
| 16:mean_soil_temperature_level_3      | double precision |      |             |            |
| 16:mean_soil_temperature_level_4      | double precision |      |             |            |
| 16:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 16:mean_surface_pressure              | double precision |      |             |            |
| 16:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 16:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 16:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 16:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 16:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 16:mean_leaf_area_index_low_vegetation | double precision|      |             |            |


</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_sat_MAMJ
- Schema: public
- Columns: 866

A table containing weekly aggregate weather data from the copernicus satellite dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of March, April, May, and June.
<details><summary>Vertical view dataset_cross_weekly_sat_MAMJ attribute list</summary>

| Attribute                             | Type             | Unit | Description | Constraint |
|---------------------------------------|------------------|------|-------------|------------|
| year                                  | bigint           |      |             |            |
| district                              | bigint           |      |             |            |
| 9:min_dewpoint_temperature           | double precision |      |             |            |
| 9:min_temperature                    | double precision |      |             |            |
| 9:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 9:min_skin_reservoir_content         | double precision |      |             |            |
| 9:min_skin_temperature               | double precision |      |             |            |
| 9:min_snowmelt                       | double precision |      |             |            |
| 9:min_soil_temperature_level_1       | double precision |      |             |            |
| 9:min_soil_temperature_level_2       | double precision |      |             |            |
| 9:min_soil_temperature_level_3       | double precision |      |             |            |
| 9:min_soil_temperature_level_4       | double precision |      |             |            |
| 9:min_surface_net_solar_radiation    | double precision |      |             |            |
| 9:min_surface_pressure               | double precision |      |             |            |
| 9:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 9:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 9:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 9:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 9:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 9:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 9:max_dewpoint_temperature           | double precision |      |             |            |
| 9:max_temperature                    | double precision |      |             |            |
| 9:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 9:max_skin_reservoir_content         | double precision |      |             |            |
| 9:max_skin_temperature               | double precision |      |             |            |
| 9:max_snowmelt                       | double precision |      |             |            |
| 9:max_soil_temperature_level_1       | double precision |      |             |            |
| 9:max_soil_temperature_level_2       | double precision |      |             |            |
| 9:max_soil_temperature_level_3       | double precision |      |             |            |
| 9:max_soil_temperature_level_4       | double precision |      |             |            |
| 9:max_surface_net_solar_radiation    | double precision |      |             |            |
| 9:max_surface_pressure               | double precision |      |             |            |
| 9:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 9:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 9:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 9:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 9:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 9:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 9:mean_dewpoint_temperature          | double precision |      |             |            |
| 9:mean_temperature                   | double precision |      |             |            |
| 9:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 9:mean_skin_reservoir_content        | double precision |      |             |            |
| 9:mean_skin_temperature              | double precision |      |             |            |
| 9:mean_snowmelt                      | double precision |      |             |            |
| 9:mean_soil_temperature_level_1      | double precision |      |             |            |
| 9:mean_soil_temperature_level_2      | double precision |      |             |            |
| 9:mean_soil_temperature_level_3      | double precision |      |             |            |
| 9:mean_soil_temperature_level_4      | double precision |      |             |            |
| 9:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 9:mean_surface_pressure              | double precision |      |             |            |
| 9:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 9:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 9:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 9:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 9:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 9:mean_leaf_area_index_low_vegetation | double precision|      |             |            |
| ...                             | ...             | ... | ... | ... |
| 24:min_dewpoint_temperature           | double precision |      |             |            |
| 24:min_temperature                    | double precision |      |             |            |
| 24:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 24:min_skin_reservoir_content         | double precision |      |             |            |
| 24:min_skin_temperature               | double precision |      |             |            |
| 24:min_snowmelt                       | double precision |      |             |            |
| 24:min_soil_temperature_level_1       | double precision |      |             |            |
| 24:min_soil_temperature_level_2       | double precision |      |             |            |
| 24:min_soil_temperature_level_3       | double precision |      |             |            |
| 24:min_soil_temperature_level_4       | double precision |      |             |            |
| 24:min_surface_net_solar_radiation    | double precision |      |             |            |
| 24:min_surface_pressure               | double precision |      |             |            |
| 24:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 24:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 24:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 24:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 24:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 24:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 24:max_dewpoint_temperature           | double precision |      |             |            |
| 24:max_temperature                    | double precision |      |             |            |
| 24:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 24:max_skin_reservoir_content         | double precision |      |             |            |
| 24:max_skin_temperature               | double precision |      |             |            |
| 24:max_snowmelt                       | double precision |      |             |            |
| 24:max_soil_temperature_level_1       | double precision |      |             |            |
| 24:max_soil_temperature_level_2       | double precision |      |             |            |
| 24:max_soil_temperature_level_3       | double precision |      |             |            |
| 24:max_soil_temperature_level_4       | double precision |      |             |            |
| 24:max_surface_net_solar_radiation    | double precision |      |             |            |
| 24:max_surface_pressure               | double precision |      |             |            |
| 24:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 24:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 24:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 24:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 24:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 24:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 24:mean_dewpoint_temperature          | double precision |      |             |            |
| 24:mean_temperature                   | double precision |      |             |            |
| 24:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 24:mean_skin_reservoir_content        | double precision |      |             |            |
| 24:mean_skin_temperature              | double precision |      |             |            |
| 24:mean_snowmelt                      | double precision |      |             |            |
| 24:mean_soil_temperature_level_1      | double precision |      |             |            |
| 24:mean_soil_temperature_level_2      | double precision |      |             |            |
| 24:mean_soil_temperature_level_3      | double precision |      |             |            |
| 24:mean_soil_temperature_level_4      | double precision |      |             |            |
| 24:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 24:mean_surface_pressure              | double precision |      |             |            |
| 24:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 24:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 24:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 24:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 24:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 24:mean_leaf_area_index_low_vegetation | double precision|      |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_sat_MJJA
- Schema: public
- Columns: 866

A table containing weekly aggregate weather data from the copernicus satellite dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of May, June, July, and August.
<details><summary>Vertical view dataset_cross_weekly_sat_MJJA attribute list</summary>

| Attribute                             | Type             | Unit | Description | Constraint |
|---------------------------------------|------------------|------|-------------|------------|
| year                                  | bigint           |      |             |            |
| district                              | bigint           |      |             |            |
| 17:min_dewpoint_temperature           | double precision |      |             |            |
| 17:min_temperature                    | double precision |      |             |            |
| 17:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 17:min_skin_reservoir_content         | double precision |      |             |            |
| 17:min_skin_temperature               | double precision |      |             |            |
| 17:min_snowmelt                       | double precision |      |             |            |
| 17:min_soil_temperature_level_1       | double precision |      |             |            |
| 17:min_soil_temperature_level_2       | double precision |      |             |            |
| 17:min_soil_temperature_level_3       | double precision |      |             |            |
| 17:min_soil_temperature_level_4       | double precision |      |             |            |
| 17:min_surface_net_solar_radiation    | double precision |      |             |            |
| 17:min_surface_pressure               | double precision |      |             |            |
| 17:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 17:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 17:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 17:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 17:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 17:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 17:max_dewpoint_temperature           | double precision |      |             |            |
| 17:max_temperature                    | double precision |      |             |            |
| 17:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 17:max_skin_reservoir_content         | double precision |      |             |            |
| 17:max_skin_temperature               | double precision |      |             |            |
| 17:max_snowmelt                       | double precision |      |             |            |
| 17:max_soil_temperature_level_1       | double precision |      |             |            |
| 17:max_soil_temperature_level_2       | double precision |      |             |            |
| 17:max_soil_temperature_level_3       | double precision |      |             |            |
| 17:max_soil_temperature_level_4       | double precision |      |             |            |
| 17:max_surface_net_solar_radiation    | double precision |      |             |            |
| 17:max_surface_pressure               | double precision |      |             |            |
| 17:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 17:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 17:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 17:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 17:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 17:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 17:mean_dewpoint_temperature          | double precision |      |             |            |
| 17:mean_temperature                   | double precision |      |             |            |
| 17:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 17:mean_skin_reservoir_content        | double precision |      |             |            |
| 17:mean_skin_temperature              | double precision |      |             |            |
| 17:mean_snowmelt                      | double precision |      |             |            |
| 17:mean_soil_temperature_level_1      | double precision |      |             |            |
| 17:mean_soil_temperature_level_2      | double precision |      |             |            |
| 17:mean_soil_temperature_level_3      | double precision |      |             |            |
| 17:mean_soil_temperature_level_4      | double precision |      |             |            |
| 17:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 17:mean_surface_pressure              | double precision |      |             |            |
| 17:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 17:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 17:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 17:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 17:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 17:mean_leaf_area_index_low_vegetation | double precision|      |             |            |
| ...                             | ...             | ... | ... | ... |
| 32:min_dewpoint_temperature           | double precision |      |             |            |
| 32:min_temperature                    | double precision |      |             |            |
| 32:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 32:min_skin_reservoir_content         | double precision |      |             |            |
| 32:min_skin_temperature               | double precision |      |             |            |
| 32:min_snowmelt                       | double precision |      |             |            |
| 32:min_soil_temperature_level_1       | double precision |      |             |            |
| 32:min_soil_temperature_level_2       | double precision |      |             |            |
| 32:min_soil_temperature_level_3       | double precision |      |             |            |
| 32:min_soil_temperature_level_4       | double precision |      |             |            |
| 32:min_surface_net_solar_radiation    | double precision |      |             |            |
| 32:min_surface_pressure               | double precision |      |             |            |
| 32:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 32:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 32:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 32:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 32:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 32:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 32:max_dewpoint_temperature           | double precision |      |             |            |
| 32:max_temperature                    | double precision |      |             |            |
| 32:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 32:max_skin_reservoir_content         | double precision |      |             |            |
| 32:max_skin_temperature               | double precision |      |             |            |
| 32:max_snowmelt                       | double precision |      |             |            |
| 32:max_soil_temperature_level_1       | double precision |      |             |            |
| 32:max_soil_temperature_level_2       | double precision |      |             |            |
| 32:max_soil_temperature_level_3       | double precision |      |             |            |
| 32:max_soil_temperature_level_4       | double precision |      |             |            |
| 32:max_surface_net_solar_radiation    | double precision |      |             |            |
| 32:max_surface_pressure               | double precision |      |             |            |
| 32:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 32:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 32:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 32:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 32:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 32:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 32:mean_dewpoint_temperature          | double precision |      |             |            |
| 32:mean_temperature                   | double precision |      |             |            |
| 32:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 32:mean_skin_reservoir_content        | double precision |      |             |            |
| 32:mean_skin_temperature              | double precision |      |             |            |
| 32:mean_snowmelt                      | double precision |      |             |            |
| 32:mean_soil_temperature_level_1      | double precision |      |             |            |
| 32:mean_soil_temperature_level_2      | double precision |      |             |            |
| 32:mean_soil_temperature_level_3      | double precision |      |             |            |
| 32:mean_soil_temperature_level_4      | double precision |      |             |            |
| 32:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 32:mean_surface_pressure              | double precision |      |             |            |
| 32:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 32:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 32:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 32:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 32:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 32:mean_leaf_area_index_low_vegetation | double precision|      |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_sat_JASO
- Schema: public
- Columns: 866

A table containing weekly aggregate weather data from the copernicus satellite dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of July, August, September, and October.
<details><summary>Vertical view dataset_cross_weekly_sat_JASO attribute list</summary>

| Attribute                             | Type             | Unit | Description | Constraint |
|---------------------------------------|------------------|------|-------------|------------|
| year                                  | bigint           |      |             |            |
| district                              | bigint           |      |             |            |
| 25:min_dewpoint_temperature           | double precision |      |             |            |
| 25:min_temperature                    | double precision |      |             |            |
| 25:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 25:min_skin_reservoir_content         | double precision |      |             |            |
| 25:min_skin_temperature               | double precision |      |             |            |
| 25:min_snowmelt                       | double precision |      |             |            |
| 25:min_soil_temperature_level_1       | double precision |      |             |            |
| 25:min_soil_temperature_level_2       | double precision |      |             |            |
| 25:min_soil_temperature_level_3       | double precision |      |             |            |
| 25:min_soil_temperature_level_4       | double precision |      |             |            |
| 25:min_surface_net_solar_radiation    | double precision |      |             |            |
| 25:min_surface_pressure               | double precision |      |             |            |
| 25:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 25:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 25:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 25:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 25:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 25:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 25:max_dewpoint_temperature           | double precision |      |             |            |
| 25:max_temperature                    | double precision |      |             |            |
| 25:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 25:max_skin_reservoir_content         | double precision |      |             |            |
| 25:max_skin_temperature               | double precision |      |             |            |
| 25:max_snowmelt                       | double precision |      |             |            |
| 25:max_soil_temperature_level_1       | double precision |      |             |            |
| 25:max_soil_temperature_level_2       | double precision |      |             |            |
| 25:max_soil_temperature_level_3       | double precision |      |             |            |
| 25:max_soil_temperature_level_4       | double precision |      |             |            |
| 25:max_surface_net_solar_radiation    | double precision |      |             |            |
| 25:max_surface_pressure               | double precision |      |             |            |
| 25:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 25:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 25:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 25:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 25:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 25:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 25:mean_dewpoint_temperature          | double precision |      |             |            |
| 25:mean_temperature                   | double precision |      |             |            |
| 25:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 25:mean_skin_reservoir_content        | double precision |      |             |            |
| 25:mean_skin_temperature              | double precision |      |             |            |
| 25:mean_snowmelt                      | double precision |      |             |            |
| 25:mean_soil_temperature_level_1      | double precision |      |             |            |
| 25:mean_soil_temperature_level_2      | double precision |      |             |            |
| 25:mean_soil_temperature_level_3      | double precision |      |             |            |
| 25:mean_soil_temperature_level_4      | double precision |      |             |            |
| 25:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 25:mean_surface_pressure              | double precision |      |             |            |
| 25:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 25:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 25:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 25:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 25:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 25:mean_leaf_area_index_low_vegetation | double precision|      |             |            |
| ...                             | ...             | ... | ... | ... |
| 40:min_dewpoint_temperature           | double precision |      |             |            |
| 40:min_temperature                    | double precision |      |             |            |
| 40:min_evaporation_from_bare_soil     | double precision |      |             |            |
| 40:min_skin_reservoir_content         | double precision |      |             |            |
| 40:min_skin_temperature               | double precision |      |             |            |
| 40:min_snowmelt                       | double precision |      |             |            |
| 40:min_soil_temperature_level_1       | double precision |      |             |            |
| 40:min_soil_temperature_level_2       | double precision |      |             |            |
| 40:min_soil_temperature_level_3       | double precision |      |             |            |
| 40:min_soil_temperature_level_4       | double precision |      |             |            |
| 40:min_surface_net_solar_radiation    | double precision |      |             |            |
| 40:min_surface_pressure               | double precision |      |             |            |
| 40:min_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 40:min_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 40:min_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 40:min_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 40:min_leaf_area_index_high_vegetation| double precision |      |             |            |
| 40:min_leaf_area_index_low_vegetation | double precision |      |             |            |
| 40:max_dewpoint_temperature           | double precision |      |             |            |
| 40:max_temperature                    | double precision |      |             |            |
| 40:max_evaporation_from_bare_soil     | double precision |      |             |            |
| 40:max_skin_reservoir_content         | double precision |      |             |            |
| 40:max_skin_temperature               | double precision |      |             |            |
| 40:max_snowmelt                       | double precision |      |             |            |
| 40:max_soil_temperature_level_1       | double precision |      |             |            |
| 40:max_soil_temperature_level_2       | double precision |      |             |            |
| 40:max_soil_temperature_level_3       | double precision |      |             |            |
| 40:max_soil_temperature_level_4       | double precision |      |             |            |
| 40:max_surface_net_solar_radiation    | double precision |      |             |            |
| 40:max_surface_pressure               | double precision |      |             |            |
| 40:max_volumetric_soil_water_layer_1  | double precision |      |             |            |
| 40:max_volumetric_soil_water_layer_2  | double precision |      |             |            |
| 40:max_volumetric_soil_water_layer_3  | double precision |      |             |            |
| 40:max_volumetric_soil_water_layer_4  | double precision |      |             |            |
| 40:max_leaf_area_index_high_vegetation| double precision |      |             |            |
| 40:max_leaf_area_index_low_vegetation | double precision |      |             |            |
| 40:mean_dewpoint_temperature          | double precision |      |             |            |
| 40:mean_temperature                   | double precision |      |             |            |
| 40:mean_evaporation_from_bare_soil    | double precision |      |             |            |
| 40:mean_skin_reservoir_content        | double precision |      |             |            |
| 40:mean_skin_temperature              | double precision |      |             |            |
| 40:mean_snowmelt                      | double precision |      |             |            |
| 40:mean_soil_temperature_level_1      | double precision |      |             |            |
| 40:mean_soil_temperature_level_2      | double precision |      |             |            |
| 40:mean_soil_temperature_level_3      | double precision |      |             |            |
| 40:mean_soil_temperature_level_4      | double precision |      |             |            |
| 40:mean_surface_net_solar_radiation   | double precision |      |             |            |
| 40:mean_surface_pressure              | double precision |      |             |            |
| 40:mean_volumetric_soil_water_layer_1 | double precision |      |             |            |
| 40:mean_volumetric_soil_water_layer_2 | double precision |      |             |            |
| 40:mean_volumetric_soil_water_layer_3 | double precision |      |             |            |
| 40:mean_volumetric_soil_water_layer_4 | double precision |      |             |            |
| 40:mean_leaf_area_index_high_vegetation| double precision|      |             |            |
| 40:mean_leaf_area_index_low_vegetation | double precision|      |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_daily_station
- Schema: public
- Columns: 40

A table containing daily aggregate weather data from the weather station dataset.
<details><summary>Vertical view dataset_daily_station attribute list</summary>

| Attribute           | Type                | Unit            | Description               | Constraint   |
|---------------------|---------------------|-----------------|---------------------------|--------------|
| district            | bigint              | N/A             | District identifier       |              |
| year                | bigint              | Year            | Year                      |              |
| month               | bigint              | Month           | Month                     |              |
| day                 | bigint              | Day             | Day                       |              |
| min_temp_x          | double precision    | Celsius         | Minimum temperature x     |              |
| max_temp_x          | double precision    | Celsius         | Maximum temperature x     |              |
| mean_temp_x         | double precision    | Celsius         | Mean temperature x        |              |
| min_dew_point_temp  | double precision    | Celsius         | Minimum dew point temp    |              |
| max_dew_point_temp  | double precision    | Celsius         | Maximum dew point temp    |              |
| mean_dew_point_temp | double precision    | Celsius         | Mean dew point temp       |              |
| min_humidex         | double precision    | N/A             | Minimum humidex           |              |
| max_humidex         | double precision    | N/A             | Maximum humidex           |              |
| mean_humidex        | double precision    | N/A             | Mean humidex              |              |
| min_precip          | double precision    | Millimeters     | Minimum precipitation     |              |
| max_precip          | double precision    | Millimeters     | Maximum precipitation     |              |
| mean_precip         | double precision    | Millimeters     | Mean precipitation        |              |
| min_rel_humid       | double precision    | Percent         | Minimum relative humidity |              |
| max_rel_humid       | double precision    | Percent         | Maximum relative humidity |              |
| mean_rel_humid      | double precision    | Percent         | Mean relative humidity    |              |
| min_stn_press       | double precision    | Kilopascals     | Minimum station pressure  |              |
| max_stn_press       | double precision    | Kilopascals     | Maximum station pressure  |              |
| mean_stn_press      | double precision    | Kilopascals     | Mean station pressure     |              |
| min_visibility      | double precision    | Kilometers      | Minimum visibility        |              |
| max_visibility      | double precision    | Kilometers      | Maximum visibility        |              |
| mean_visibility     | double precision    | Kilometers      | Mean visibility           |              |
| max_temp_y          | double precision    | Celsius         | Maximum temperature y     |              |
| min_temp_y          | double precision    | Celsius         | Minimum temperature y     |              |
| mean_temp_y         | double precision    | Celsius         | Mean temperature y        |              |
| min_total_rain      | double precision    | Millimeters     | Minimum total rain        |              |
| max_total_rain      | double precision    | Millimeters     | Maximum total rain        |              |
| mean_total_rain     | double precision    | Millimeters     | Mean total rain           |              |
| min_total_snow      | double precision    | Centimeters     | Minimum total snow        |              |
| max_total_snow      | double precision    | Centimeters     | Maximum total snow        |              |
| mean_total_snow     | double precision    | Centimeters     | Mean total snow           |              |
| min_total_precip    | double precision    | Millimeters     | Minimum total precipitation |              |
| max_total_precip    | double precision    | Millimeters     | Maximum total precipitation |              |
| mean_total_precip   | double precision    | Millimeters     | Mean total precipitation  |              |
| min_snow_on_grnd    | double precision    | Centimeters     | Minimum snow on ground    |              |
| max_snow_on_grnd    | double precision    | Centimeters     | Maximum snow on ground    |              |
| mean_snow_on_grnd   | double precision    | Centimeters     | Mean snow on ground       |              |

</details>

[back to top](#overview)
<br>
<br>

### dataset_weekly_station
- Schema: public
- Columns: 40

A table containing weekly aggregate weather data from the weather station dataset.
<details><summary>Vertical view dataset_weekly_station attribute list</summary>

| Attribute           | Type                | Unit            | Description               | Constraint   |
|---------------------|---------------------|-----------------|---------------------------|--------------|
| year                | bigint              | Year            | Year                      |              |
| month               | bigint              | Month           | Month                     |              |
| week_of_year        | bigint              | Week            | Week of the year          |              |
| district            | bigint              | N/A             | District identifier       |              |
| min_temp_x          | double precision    | Celsius         | Minimum temperature x     |              |
| max_temp_x          | double precision    | Celsius         | Maximum temperature x     |              |
| mean_temp_x         | double precision    | Celsius         | Mean temperature x        |              |
| min_dew_point_temp  | double precision    | Celsius         | Minimum dew point temp    |              |
| max_dew_point_temp  | double precision    | Celsius         | Maximum dew point temp    |              |
| mean_dew_point_temp | double precision    | Celsius         | Mean dew point temp       |              |
| min_humidex         | double precision    | N/A             | Minimum humidex           |              |
| max_humidex         | double precision    | N/A             | Maximum humidex           |              |
| mean_humidex        | double precision    | N/A             | Mean humidex              |              |
| min_precip          | double precision    | Millimeters     | Minimum precipitation     |              |
| max_precip          | double precision    | Millimeters     | Maximum precipitation     |              |
| mean_precip         | double precision    | Millimeters     | Mean precipitation        |              |
| min_rel_humid       | double precision    | Percent         | Minimum relative humidity |              |
| max_rel_humid       | double precision    | Percent         | Maximum relative humidity |              |
| mean_rel_humid      | double precision    | Percent         | Mean relative humidity    |              |
| min_stn_press       | double precision    | Kilopascals     | Minimum station pressure  |              |
| max_stn_press       | double precision    | Kilopascals     | Maximum station pressure  |              |
| mean_stn_press      | double precision    | Kilopascals     | Mean station pressure     |              |
| min_visibility      | double precision    | Kilometers      | Minimum visibility        |              |
| max_visibility      | double precision    | Kilometers      | Maximum visibility        |              |
| mean_visibility     | double precision    | Kilometers      | Mean visibility           |              |
| max_temp_y          | double precision    | Celsius         | Maximum temperature y     |              |
| min_temp_y          | double precision    | Celsius         | Minimum temperature y     |              |
| mean_temp_y         | double precision    | Celsius         | Mean temperature y        |              |
| min_total_rain      | double precision    | Millimeters     | Minimum total rain        |              |
| max_total_rain      | double precision    | Millimeters     | Maximum total rain        |              |
| mean_total_rain     | double precision    | Millimeters     | Mean total rain           |              |
| min_total_snow      | double precision    | Centimeters     | Minimum total snow        |              |
| max_total_snow      | double precision    | Centimeters     | Maximum total snow        |              |
| mean_total_snow     | double precision    | Centimeters     | Mean total snow           |              |
| min_total_precip    | double precision    | Millimeters     | Minimum total precipitation |              |
| max_total_precip    | double precision    | Millimeters     | Maximum total precipitation |              |
| mean_total_precip   | double precision    | Millimeters     | Mean total precipitation  |              |
| min_snow_on_grnd    | double precision    | Centimeters     | Minimum snow on ground    |              |
| max_snow_on_grnd    | double precision    | Centimeters     | Maximum snow on ground    |              |
| mean_snow_on_grnd   | double precision    | Centimeters     | Mean snow on ground       |              |

</details>

[back to top](#overview)
<br>
<br>

### dataset_monthly_station
- Schema: public
- Columns: 39

A table containing monthly aggregate weather data from the weather station dataset.
<details><summary>Vertical view dataset_monthly_station attribute list</summary>

| Attribute           | Type                | Unit            | Description               | Constraint   |
|---------------------|---------------------|-----------------|---------------------------|--------------|
| year                | bigint              | Year            | Year                      |              |
| month               | bigint              | Month           | Month                     |              |
| district            | bigint              | N/A             | District identifier       |              |
| min_temp_x          | double precision    | Celsius         | Minimum temperature x     |              |
| max_temp_x          | double precision    | Celsius         | Maximum temperature x     |              |
| mean_temp_x         | double precision    | Celsius         | Mean temperature x        |              |
| min_dew_point_temp  | double precision    | Celsius         | Minimum dew point temp    |              |
| max_dew_point_temp  | double precision    | Celsius         | Maximum dew point temp    |              |
| mean_dew_point_temp | double precision    | Celsius         | Mean dew point temp       |              |
| min_humidex         | double precision    | N/A             | Minimum humidex           |              |
| max_humidex         | double precision    | N/A             | Maximum humidex           |              |
| mean_humidex        | double precision    | N/A             | Mean humidex              |              |
| min_precip          | double precision    | Millimeters     | Minimum precipitation     |              |
| max_precip          | double precision    | Millimeters     | Maximum precipitation     |              |
| mean_precip         | double precision    | Millimeters     | Mean precipitation        |              |
| min_rel_humid       | double precision    | Percent         | Minimum relative humidity |              |
| max_rel_humid       | double precision    | Percent         | Maximum relative humidity |              |
| mean_rel_humid      | double precision    | Percent         | Mean relative humidity    |              |
| min_stn_press       | double precision    | Kilopascals     | Minimum station pressure  |              |
| max_stn_press       | double precision    | Kilopascals     | Maximum station pressure  |              |
| mean_stn_press      | double precision    | Kilopascals     | Mean station pressure     |              |
| min_visibility      | double precision    | Kilometers      | Minimum visibility        |              |
| max_visibility      | double precision    | Kilometers      | Maximum visibility        |              |
| mean_visibility     | double precision    | Kilometers      | Mean visibility           |              |
| max_temp_y          | double precision    | Celsius         | Maximum temperature y     |              |
| min_temp_y          | double precision    | Celsius         | Minimum temperature y     |              |
| mean_temp_y         | double precision    | Celsius         | Mean temperature y        |              |
| min_total_rain      | double precision    | Millimeters     | Minimum total rain        |              |
| max_total_rain      | double precision    | Millimeters     | Maximum total rain        |              |
| mean_total_rain     | double precision    | Millimeters     | Mean total rain           |              |
| min_total_snow      | double precision    | Centimeters     | Minimum total snow        |              |
| max_total_snow      | double precision    | Centimeters     | Maximum total snow        |              |
| mean_total_snow     | double precision    | Centimeters     | Mean total snow           |              |
| min_total_precip    | double precision    | Millimeters     | Minimum total precipitation |              |
| max_total_precip    | double precision    | Millimeters     | Maximum total precipitation |              |
| mean_total_precip   | double precision    | Millimeters     | Mean total precipitation  |              |
| min_snow_on_grnd    | double precision    | Centimeters     | Minimum snow on ground    |              |
| max_snow_on_grnd    | double precision    | Centimeters     | Maximum snow on ground    |              |
| mean_snow_on_grnd   | double precision    | Centimeters     | Mean snow on ground       |              |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_monthly_station
- Schema: public
- Columns: 434

A table containing monthly aggregate weather data from the weather station dataset. The data is crossed by the month to help determine the importance of each parameter of each month is to the model.
<details><summary>Vertical view dataset_cross_monthly_station attribute list</summary>

| Attribute           | Type                | Unit            | Description               | Constraint   |
|---------------------|---------------------|-----------------|---------------------------|--------------|
| year                | bigint              | Year            | Year                      |              |
| district            | bigint              | N/A             | District identifier       |              |
| 1:min_temp_x        | double precision    | Celsius         | Minimum temperature x     |              |
| 1:max_temp_x        | double precision    | Celsius         | Maximum temperature x     |              |
| 1:mean_temp_x       | double precision    | Celsius         | Mean temperature x        |              |
| 1:min_dew_point_temp| double precision    | Celsius         | Minimum dew point temp    |              |
| 1:max_dew_point_temp| double precision    | Celsius         | Maximum dew point temp    |              |
| 1:mean_dew_point_temp|double precision    | Celsius         | Mean dew point temp       |              |
| 1:min_humidex       | double precision    | N/A             | Minimum humidex           |              |
| 1:max_humidex       | double precision    | N/A             | Maximum humidex           |              |
| 1:mean_humidex      | double precision    | N/A             | Mean humidex              |              |
| 1:min_precip        | double precision    | Millimeters     | Minimum precipitation     |              |
| 1:max_precip        | double precision    | Millimeters     | Maximum precipitation     |              |
| 1:mean_precip       | double precision    | Millimeters     | Mean precipitation        |              |
| 1:min_rel_humid     | double precision    | Percent         | Minimum relative humidity |              |
| 1:max_rel_humid     | double precision    | Percent         | Maximum relative humidity |              |
| 1:mean_rel_humid    | double precision    | Percent         | Mean relative humidity    |              |
| 1:min_stn_press     | double precision    | Kilopascals     | Minimum station pressure  |              |
| 1:max_stn_press     | double precision    | Kilopascals     | Maximum station pressure  |              |
| 1:mean_stn_press    | double precision    | Kilopascals     | Mean station pressure     |              |
| 1:min_visibility    | double precision    | Kilometers      | Minimum visibility        |              |
| 1:max_visibility    | double precision    | Kilometers      | Maximum visibility        |              |
| 1:mean_visibility   | double precision    | Kilometers      | Mean visibility           |              |
| 1:max_temp_y        | double precision    | Celsius         | Maximum temperature y     |              |
| 1:min_temp_y        | double precision    | Celsius         | Minimum temperature y     |              |
| 1:mean_temp_y       | double precision    | Celsius         | Mean temperature y        |              |
| 1:min_total_rain    | double precision    | Millimeters     | Minimum total rain        |              |
| 1:max_total_rain    | double precision    | Millimeters     | Maximum total rain        |              |
| 1:mean_total_rain   | double precision    | Millimeters     | Mean total rain           |              |
| 1:min_total_snow    | double precision    | Centimeters     | Minimum total snow        |              |
| 1:max_total_snow    | double precision    | Centimeters     | Maximum total snow        |              |
| 1:mean_total_snow   | double precision    | Centimeters     | Mean total snow           |              |
| 1:min_total_precip  | double precision    | Millimeters     | Minimum total precipitation |              |
| 1:max_total_precip  | double precision    | Millimeters     | Maximum total precipitation |              |
| 1:mean_total_precip | double precision    | Millimeters     | Mean total precipitation  |              |
| 1:min_snow_on_grnd  | double precision    | Centimeters     | Minimum snow on ground    |              |
| 1:max_snow_on_grnd  | double precision    | Centimeters     | Maximum snow on ground    |              |
| 1:mean_snow_on_grnd | double precision    | Centimeters     | Mean snow on ground       |              |
| ...           | ...                | ...            | ...               | ...   |
| 12:min_temp_x        | double precision    | Celsius         | Minimum temperature x     |              |
| 12:max_temp_x        | double precision    | Celsius         | Maximum temperature x     |              |
| 12:mean_temp_x       | double precision    | Celsius         | Mean temperature x        |              |
| 12:min_dew_point_temp| double precision    | Celsius         | Minimum dew point temp    |              |
| 12:max_dew_point_temp| double precision    | Celsius         | Maximum dew point temp    |              |
| 12:mean_dew_point_temp|double precision    | Celsius         | Mean dew point temp       |              |
| 12:min_humidex       | double precision    | N/A             | Minimum humidex           |              |
| 12:max_humidex       | double precision    | N/A             | Maximum humidex           |              |
| 12:mean_humidex      | double precision    | N/A             | Mean humidex              |              |
| 12:min_precip        | double precision    | Millimeters     | Minimum precipitation     |              |
| 12:max_precip        | double precision    | Millimeters     | Maximum precipitation     |              |
| 12:mean_precip       | double precision    | Millimeters     | Mean precipitation        |              |
| 12:min_rel_humid     | double precision    | Percent         | Minimum relative humidity |              |
| 12:max_rel_humid     | double precision    | Percent         | Maximum relative humidity |              |
| 12:mean_rel_humid    | double precision    | Percent         | Mean relative humidity    |              |
| 12:min_stn_press     | double precision    | Kilopascals     | Minimum station pressure  |              |
| 12:max_stn_press     | double precision    | Kilopascals     | Maximum station pressure  |              |
| 12:mean_stn_press    | double precision    | Kilopascals     | Mean station pressure     |              |
| 12:min_visibility    | double precision    | Kilometers      | Minimum visibility        |              |
| 12:max_visibility    | double precision    | Kilometers      | Maximum visibility        |              |
| 12:mean_visibility   | double precision    | Kilometers      | Mean visibility           |              |
| 12:max_temp_y        | double precision    | Celsius         | Maximum temperature y     |              |
| 12:min_temp_y        | double precision    | Celsius         | Minimum temperature y     |              |
| 12:mean_temp_y       | double precision    | Celsius         | Mean temperature y        |              |
| 12:min_total_rain    | double precision    | Millimeters     | Minimum total rain        |              |
| 12:max_total_rain    | double precision    | Millimeters     | Maximum total rain        |              |
| 12:mean_total_rain   | double precision    | Millimeters     | Mean total rain           |              |
| 12:min_total_snow    | double precision    | Centimeters     | Minimum total snow        |              |
| 12:max_total_snow    | double precision    | Centimeters     | Maximum total snow        |              |
| 12:mean_total_snow   | double precision    | Centimeters     | Mean total snow           |              |
| 12:min_total_precip  | double precision    | Millimeters     | Minimum total precipitation |              |
| 12:max_total_precip  | double precision    | Millimeters     | Maximum total precipitation |              |
| 12:mean_total_precip | double precision    | Millimeters     | Mean total precipitation  |              |
| 12:min_snow_on_grnd  | double precision    | Centimeters     | Minimum snow on ground    |              |
| 12:max_snow_on_grnd  | double precision    | Centimeters     | Maximum snow on ground    |              |
| 12:mean_snow_on_grnd | double precision    | Centimeters     | Mean snow on ground       |              |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_station_JFMA
- Schema: public
- Columns: 578

A table containing weekly aggregate weather data from the weather station dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of January, February, March, and April.
<details><summary>Vertical view dataset_cross_weekly_station_JFMA attribute list</summary>

| Attribute             | Type                | Unit | Description | Constraint |
| --------------------- | ------------------- | ---- | ----------- | ---------- |
| year                  | bigint              | -    |             |            |
| district              | bigint              | -    |             |            |
| 1:min_temp_x          | double precision    | °C   |             |            |
| 1:max_temp_x          | double precision    | °C   |             |            |
| 1:mean_temp_x         | double precision    | °C   |             |            |
| 1:min_dew_point_temp  | double precision    | °C   |             |            |
| 1:max_dew_point_temp  | double precision    | °C   |             |            |
| 1:mean_dew_point_temp | double precision    | °C   |             |            |
| 1:min_humidex         | double precision    | -    |             |            |
| 1:max_humidex         | double precision    | -    |             |            |
| 1:mean_humidex        | double precision    | -    |             |            |
| 1:min_precip          | double precision    | mm   |             |            |
| 1:max_precip          | double precision    | mm   |             |            |
| 1:mean_precip         | double precision    | mm   |             |            |
| 1:min_rel_humid       | double precision    | %    |             |            |
| 1:max_rel_humid       | double precision    | %    |             |            |
| 1:mean_rel_humid      | double precision    | %    |             |            |
| 1:min_stn_press       | double precision    | kPa  |             |            |
| 1:max_stn_press       | double precision    | kPa  |             |            |
| 1:mean_stn_press      | double precision    | kPa  |             |            |
| 1:min_visibility      | double precision    | km   |             |            |
| 1:max_visibility      | double precision    | km   |             |            |
| 1:mean_visibility     | double precision    | km   |             |            |
| 1:max_temp_y          | double precision    | °C   |             |            |
| 1:min_temp_y          | double precision    | °C   |             |            |
| 1:mean_temp_y         | double precision    | °C   |             |            |
| 1:min_total_rain      | double precision    | mm   |             |            |
| 1:max_total_rain      | double precision    | mm   |             |            |
| 1:mean_total_rain     | double precision    | mm   |             |            |
| 1:min_total_snow      | double precision    | cm   |             |            |
| 1:max_total_snow      | double precision    | cm   |             |            |
| 1:mean_total_snow     | double precision    | cm   |             |            |
| 1:min_total_precip    | double precision    | mm   |             |            |
| 1:max_total_precip    | double precision    | mm   |             |            |
| 1:mean_total_precip   | double precision    | mm   |             |            |
| 1:min_snow_on_grnd    | double precision    | cm   |             |            |
| 1:max_snow_on_grnd    | double precision    | cm   |             |            |
| 1:mean_snow_on_grnd   | double precision    | cm   |             |            |
| ...             | ...                | ... | ... | ... |
| 16:min_temp_x          | double precision    | °C   |             |            |
| 16:max_temp_x          | double precision    | °C   |             |            |
| 16:mean_temp_x         | double precision    | °C   |             |            |
| 16:min_dew_point_temp  | double precision    | °C   |             |            |
| 16:max_dew_point_temp  | double precision    | °C   |             |            |
| 16:mean_dew_point_temp | double precision    | °C   |             |            |
| 16:min_humidex         | double precision    | -    |             |            |
| 16:max_humidex         | double precision    | -    |             |            |
| 16:mean_humidex        | double precision    | -    |             |            |
| 16:min_precip          | double precision    | mm   |             |            |
| 16:max_precip          | double precision    | mm   |             |            |
| 16:mean_precip         | double precision    | mm   |             |            |
| 16:min_rel_humid       | double precision    | %    |             |            |
| 16:max_rel_humid       | double precision    | %    |             |            |
| 16:mean_rel_humid      | double precision    | %    |             |            |
| 16:min_stn_press       | double precision    | kPa  |             |            |
| 16:max_stn_press       | double precision    | kPa  |             |            |
| 16:mean_stn_press      | double precision    | kPa  |             |            |
| 16:min_visibility      | double precision    | km   |             |            |
| 16:max_visibility      | double precision    | km   |             |            |
| 16:mean_visibility     | double precision    | km   |             |            |
| 16:max_temp_y          | double precision    | °C   |             |            |
| 16:min_temp_y          | double precision    | °C   |             |            |
| 16:mean_temp_y         | double precision    | °C   |             |            |
| 16:min_total_rain      | double precision    | mm   |             |            |
| 16:max_total_rain      | double precision    | mm   |             |            |
| 16:mean_total_rain     | double precision    | mm   |             |            |
| 16:min_total_snow      | double precision    | cm   |             |            |
| 16:max_total_snow      | double precision    | cm   |             |            |
| 16:mean_total_snow     | double precision    | cm   |             |            |
| 16:min_total_precip    | double precision    | mm   |             |            |
| 16:max_total_precip    | double precision    | mm   |             |            |
| 16:mean_total_precip   | double precision    | mm   |             |            |
| 16:min_snow_on_grnd    | double precision    | cm   |             |            |
| 16:max_snow_on_grnd    | double precision    | cm   |             |            |
| 16:mean_snow_on_grnd   | double precision    | cm   |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_station_MAMJ
- Schema: public
- Columns: 578

A table containing weekly aggregate weather data from the weather station dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of March, April, May, and June.
<details><summary>Vertical view dataset_cross_weekly_station_MAMJ attribute list</summary>

| Attribute             | Type                | Unit | Description | Constraint |
| --------------------- | ------------------- | ---- | ----------- | ---------- |
| year                  | bigint              | -    |             |            |
| district              | bigint              | -    |             |            |
| 9:min_temp_x          | double precision    | °C   |             |            |
| 9:max_temp_x          | double precision    | °C   |             |            |
| 9:mean_temp_x         | double precision    | °C   |             |            |
| 9:min_dew_point_temp  | double precision    | °C   |             |            |
| 9:max_dew_point_temp  | double precision    | °C   |             |            |
| 9:mean_dew_point_temp | double precision    | °C   |             |            |
| 9:min_humidex         | double precision    | -    |             |            |
| 9:max_humidex         | double precision    | -    |             |            |
| 9:mean_humidex        | double precision    | -    |             |            |
| 9:min_precip          | double precision    | mm   |             |            |
| 9:max_precip          | double precision    | mm   |             |            |
| 9:mean_precip         | double precision    | mm   |             |            |
| 9:min_rel_humid       | double precision    | %    |             |            |
| 9:max_rel_humid       | double precision    | %    |             |            |
| 9:mean_rel_humid      | double precision    | %    |             |            |
| 9:min_stn_press       | double precision    | kPa  |             |            |
| 9:max_stn_press       | double precision    | kPa  |             |            |
| 9:mean_stn_press      | double precision    | kPa  |             |            |
| 9:min_visibility      | double precision    | km   |             |            |
| 9:max_visibility      | double precision    | km   |             |            |
| 9:mean_visibility     | double precision    | km   |             |            |
| 9:max_temp_y          | double precision    | °C   |             |            |
| 9:min_temp_y          | double precision    | °C   |             |            |
| 9:mean_temp_y         | double precision    | °C   |             |            |
| 9:min_total_rain      | double precision    | mm   |             |            |
| 9:max_total_rain      | double precision    | mm   |             |            |
| 9:mean_total_rain     | double precision    | mm   |             |            |
| 9:min_total_snow      | double precision    | cm   |             |            |
| 9:max_total_snow      | double precision    | cm   |             |            |
| 9:mean_total_snow     | double precision    | cm   |             |            |
| 9:min_total_precip    | double precision    | mm   |             |            |
| 9:max_total_precip    | double precision    | mm   |             |            |
| 9:mean_total_precip   | double precision    | mm   |             |            |
| 9:min_snow_on_grnd    | double precision    | cm   |             |            |
| 9:max_snow_on_grnd    | double precision    | cm   |             |            |
| 9:mean_snow_on_grnd   | double precision    | cm   |             |            |
| ...             | ...                | ... | ... | ... |
| 24:min_temp_x          | double precision    | °C   |             |            |
| 24:max_temp_x          | double precision    | °C   |             |            |
| 24:mean_temp_x         | double precision    | °C   |             |            |
| 24:min_dew_point_temp  | double precision    | °C   |             |            |
| 24:max_dew_point_temp  | double precision    | °C   |             |            |
| 24:mean_dew_point_temp | double precision    | °C   |             |            |
| 24:min_humidex         | double precision    | -    |             |            |
| 24:max_humidex         | double precision    | -    |             |            |
| 24:mean_humidex        | double precision    | -    |             |            |
| 24:min_precip          | double precision    | mm   |             |            |
| 24:max_precip          | double precision    | mm   |             |            |
| 24:mean_precip         | double precision    | mm   |             |            |
| 24:min_rel_humid       | double precision    | %    |             |            |
| 24:max_rel_humid       | double precision    | %    |             |            |
| 24:mean_rel_humid      | double precision    | %    |             |            |
| 24:min_stn_press       | double precision    | kPa  |             |            |
| 24:max_stn_press       | double precision    | kPa  |             |            |
| 24:mean_stn_press      | double precision    | kPa  |             |            |
| 24:min_visibility      | double precision    | km   |             |            |
| 24:max_visibility      | double precision    | km   |             |            |
| 24:mean_visibility     | double precision    | km   |             |            |
| 24:max_temp_y          | double precision    | °C   |             |            |
| 24:min_temp_y          | double precision    | °C   |             |            |
| 24:mean_temp_y         | double precision    | °C   |             |            |
| 24:min_total_rain      | double precision    | mm   |             |            |
| 24:max_total_rain      | double precision    | mm   |             |            |
| 24:mean_total_rain     | double precision    | mm   |             |            |
| 24:min_total_snow      | double precision    | cm   |             |            |
| 24:max_total_snow      | double precision    | cm   |             |            |
| 24:mean_total_snow     | double precision    | cm   |             |            |
| 24:min_total_precip    | double precision    | mm   |             |            |
| 24:max_total_precip    | double precision    | mm   |             |            |
| 24:mean_total_precip   | double precision    | mm   |             |            |
| 24:min_snow_on_grnd    | double precision    | cm   |             |            |
| 24:max_snow_on_grnd    | double precision    | cm   |             |            |
| 24:mean_snow_on_grnd   | double precision    | cm   |             |            |
</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_station_MJJA
- Schema: public
- Columns: 578

A table containing weekly aggregate weather data from the weather station dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of May, June, July, and August.
<details><summary>Vertical view dataset_cross_weekly_station_MJJA attribute list</summary>

| Attribute             | Type                | Unit | Description | Constraint |
| --------------------- | ------------------- | ---- | ----------- | ---------- |
| year                  | bigint              | -    |             |            |
| district              | bigint              | -    |             |            |
| 17:min_temp_x          | double precision    | °C   |             |            |
| 17:max_temp_x          | double precision    | °C   |             |            |
| 17:mean_temp_x         | double precision    | °C   |             |            |
| 17:min_dew_point_temp  | double precision    | °C   |             |            |
| 17:max_dew_point_temp  | double precision    | °C   |             |            |
| 17:mean_dew_point_temp | double precision    | °C   |             |            |
| 17:min_humidex         | double precision    | -    |             |            |
| 17:max_humidex         | double precision    | -    |             |            |
| 17:mean_humidex        | double precision    | -    |             |            |
| 17:min_precip          | double precision    | mm   |             |            |
| 17:max_precip          | double precision    | mm   |             |            |
| 17:mean_precip         | double precision    | mm   |             |            |
| 17:min_rel_humid       | double precision    | %    |             |            |
| 17:max_rel_humid       | double precision    | %    |             |            |
| 17:mean_rel_humid      | double precision    | %    |             |            |
| 17:min_stn_press       | double precision    | kPa  |             |            |
| 17:max_stn_press       | double precision    | kPa  |             |            |
| 17:mean_stn_press      | double precision    | kPa  |             |            |
| 17:min_visibility      | double precision    | km   |             |            |
| 17:max_visibility      | double precision    | km   |             |            |
| 17:mean_visibility     | double precision    | km   |             |            |
| 17:max_temp_y          | double precision    | °C   |             |            |
| 17:min_temp_y          | double precision    | °C   |             |            |
| 17:mean_temp_y         | double precision    | °C   |             |            |
| 17:min_total_rain      | double precision    | mm   |             |            |
| 17:max_total_rain      | double precision    | mm   |             |            |
| 17:mean_total_rain     | double precision    | mm   |             |            |
| 17:min_total_snow      | double precision    | cm   |             |            |
| 17:max_total_snow      | double precision    | cm   |             |            |
| 17:mean_total_snow     | double precision    | cm   |             |            |
| 17:min_total_precip    | double precision    | mm   |             |            |
| 17:max_total_precip    | double precision    | mm   |             |            |
| 17:mean_total_precip   | double precision    | mm   |             |            |
| 17:min_snow_on_grnd    | double precision    | cm   |             |            |
| 17:max_snow_on_grnd    | double precision    | cm   |             |            |
| 17:mean_snow_on_grnd   | double precision    | cm   |             |            |
| ...             | ...                | ... | ... | ... |
| 32:min_temp_x          | double precision    | °C   |             |            |
| 32:max_temp_x          | double precision    | °C   |             |            |
| 32:mean_temp_x         | double precision    | °C   |             |            |
| 32:min_dew_point_temp  | double precision    | °C   |             |            |
| 32:max_dew_point_temp  | double precision    | °C   |             |            |
| 32:mean_dew_point_temp | double precision    | °C   |             |            |
| 32:min_humidex         | double precision    | -    |             |            |
| 32:max_humidex         | double precision    | -    |             |            |
| 32:mean_humidex        | double precision    | -    |             |            |
| 32:min_precip          | double precision    | mm   |             |            |
| 32:max_precip          | double precision    | mm   |             |            |
| 32:mean_precip         | double precision    | mm   |             |            |
| 32:min_rel_humid       | double precision    | %    |             |            |
| 32:max_rel_humid       | double precision    | %    |             |            |
| 32:mean_rel_humid      | double precision    | %    |             |            |
| 32:min_stn_press       | double precision    | kPa  |             |            |
| 32:max_stn_press       | double precision    | kPa  |             |            |
| 32:mean_stn_press      | double precision    | kPa  |             |            |
| 32:min_visibility      | double precision    | km   |             |            |
| 32:max_visibility      | double precision    | km   |             |            |
| 32:mean_visibility     | double precision    | km   |             |            |
| 32:max_temp_y          | double precision    | °C   |             |            |
| 32:min_temp_y          | double precision    | °C   |             |            |
| 32:mean_temp_y         | double precision    | °C   |             |            |
| 32:min_total_rain      | double precision    | mm   |             |            |
| 32:max_total_rain      | double precision    | mm   |             |            |
| 32:mean_total_rain     | double precision    | mm   |             |            |
| 32:min_total_snow      | double precision    | cm   |             |            |
| 32:max_total_snow      | double precision    | cm   |             |            |
| 32:mean_total_snow     | double precision    | cm   |             |            |
| 32:min_total_precip    | double precision    | mm   |             |            |
| 32:max_total_precip    | double precision    | mm   |             |            |
| 32:mean_total_precip   | double precision    | mm   |             |            |
| 32:min_snow_on_grnd    | double precision    | cm   |             |            |
| 32:max_snow_on_grnd    | double precision    | cm   |             |            |
| 32:mean_snow_on_grnd   | double precision    | cm   |             |            |
</details>

[back to top](#overview)
<br>
<br>

### dataset_cross_weekly_station_JASO
- Schema: public
- Columns: 578

A table containing weekly aggregate weather data from the weather station dataset. The data is crossed by the week of year to help determine the importance of each parameter of each week is to the model. This table only contains data from the months of July, August, September, and October.
<details><summary>Vertical view dataset_cross_weekly_station_JASO attribute list</summary>

| Attribute               | Type                | Unit | Description | Constraint |
| ----------------------- | ------------------- | ---- | ----------- | ---------- |
| year                    | bigint              | -    |             |            |
| district                | bigint              | -    |             |            |
| 25:min_temp_x           | double precision    | °C   |             |            |
| 25:max_temp_x           | double precision    | °C   |             |            |
| 25:mean_temp_x          | double precision    | °C   |             |            |
| 25:min_dew_point_temp   | double precision    | °C   |             |            |
| 25:max_dew_point_temp   | double precision    | °C   |             |            |
| 25:mean_dew_point_temp  | double precision    | °C   |             |            |
| 25:min_humidex          | double precision    | -    |             |            |
| 25:max_humidex          | double precision    | -    |             |            |
| 25:mean_humidex         | double precision    | -    |             |            |
| 25:min_precip           | double precision    | mm   |             |            |
| 25:max_precip           | double precision    | mm   |             |            |
| 25:mean_precip          | double precision    | mm   |             |            |
| 25:min_rel_humid        | double precision    | %    |             |            |
| 25:max_rel_humid        | double precision    | %    |             |            |
| 25:mean_rel_humid       | double precision    | %    |             |            |
| 25:min_stn_press        | double precision    | kPa  |             |            |
| 25:max_stn_press        | double precision    | kPa  |             |            |
| 25:mean_stn_press       | double precision    | kPa  |             |            |
| 25:min_visibility       | double precision    | km   |             |            |
| 25:max_visibility       | double precision    | km   |             |            |
| 25:mean_visibility      | double precision    | km   |             |            |
| 25:max_temp_y           | double precision    | °C   |             |            |
| 25:min_temp_y           | double precision    | °C   |             |            |
| 25:mean_temp_y          | double precision    | °C   |             |            |
| 25:min_total_rain       | double precision    | mm   |             |            |
| 25:max_total_rain       | double precision    | mm   |             |            |
| 25:mean_total_rain      | double precision    | mm   |             |            |
| 25:min_total_snow       | double precision    | cm   |             |            |
| 25:max_total_snow       | double precision    | cm   |             |            |
| 25:mean_total_snow      | double precision    | cm   |             |            |
| 25:min_total_precip     | double precision    | mm   |             |            |
| 25:max_total_precip     | double precision    | mm   |             |            |
| 25:mean_total_precip    | double precision    | mm   |             |            |
| 25:min_snow_on_grnd     | double precision    | cm   |             |            |
| 25:max_snow_on_grnd     | double precision    | cm   |             |            |
| 25:mean_snow_on_grnd    | double precision    | cm   |             |            |
| ...             | ...                | ... | ... | ... |
| 40:min_temp_x          | double precision    | °C   |             |            |
| 40:max_temp_x          | double precision    | °C   |             |            |
| 40:mean_temp_x         | double precision    | °C   |             |            |
| 40:min_dew_point_temp  | double precision    | °C   |             |            |
| 40:max_dew_point_temp  | double precision    | °C   |             |            |
| 40:mean_dew_point_temp | double precision    | °C   |             |            |
| 40:min_humidex         | double precision    | -    |             |            |
| 40:max_humidex         | double precision    | -    |             |            |
| 40:mean_humidex        | double precision    | -    |             |            |
| 40:min_precip          | double precision    | mm   |             |            |
| 40:max_precip          | double precision    | mm   |             |            |
| 40:mean_precip         | double precision    | mm   |             |            |
| 40:min_rel_humid       | double precision    | %    |             |            |
| 40:max_rel_humid       | double precision    | %    |             |            |
| 40:mean_rel_humid      | double precision    | %    |             |            |
| 40:min_stn_press       | double precision    | kPa  |             |            |
| 40:max_stn_press       | double precision    | kPa  |             |            |
| 40:mean_stn_press      | double precision    | kPa  |             |            |
| 40:min_visibility      | double precision    | km   |             |            |
| 40:max_visibility      | double precision    | km   |             |            |
| 40:mean_visibility     | double precision    | km   |             |            |
| 40:max_temp_y          | double precision    | °C   |             |            |
| 40:min_temp_y          | double precision    | °C   |             |            |
| 40:mean_temp_y         | double precision    | °C   |             |            |
| 40:min_total_rain      | double precision    | mm   |             |            |
| 40:max_total_rain      | double precision    | mm   |             |            |
| 40:mean_total_rain     | double precision    | mm   |             |            |
| 40:min_total_snow      | double precision    | cm   |             |            |
| 40:max_total_snow      | double precision    | cm   |             |            |
| 40:mean_total_snow     | double precision    | cm   |             |            |
| 40:min_total_precip    | double precision    | mm   |             |            |
| 40:max_total_precip    | double precision    | mm   |             |            |
| 40:mean_total_precip   | double precision    | mm   |             |            |
| 40:min_snow_on_grnd    | double precision    | cm   |             |            |
| 40:max_snow_on_grnd    | double precision    | cm   |             |            |
| 40:mean_snow_on_grnd   | double precision    | cm   |             |            |
</details>

[back to top](#overview)
<br>
<br>

### dataset_daily_sat_soil
- Schema: public
- Columns: 65

A table containing daily aggregate weather data from the copernicus satellite dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_daily_sat_soil attribute list</summary>

| Attribute                           | Type              | Unit | Description | Constraint |
| ----------------------------------- | ----------------- | ---- | ----------- | ---------- |
| year                                | bigint            | -    |             |            |
| month_x                             | bigint            | -    |             |            |
| day_x                               | bigint            | -    |             |            |
| cr_num                              | bigint            | -    |             |            |
| district                            | bigint            | -    |             |            |
| min_dewpoint_temperature            | double precision  | °C   |             |            |
| max_dewpoint_temperature            | double precision  | °C   |             |            |
| mean_dewpoint_temperature           | double precision  | °C   |             |            |
| min_temperature                     | double precision  | °C   |             |            |
| max_temperature                     | double precision  | °C   |             |            |
| mean_temperature                    | double precision  | °C   |             |            |
| min_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| max_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| mean_evaporation_from_bare_soil     | double precision  | mm   |             |            |
| min_skin_reservoir_content          | double precision  | mm   |             |            |
| max_skin_reservoir_content          | double precision  | mm   |             |            |
| mean_skin_reservoir_content         | double precision  | mm   |             |            |
| min_skin_temperature                | double precision  | °C   |             |            |
| max_skin_temperature                | double precision  | °C   |             |            |
| mean_skin_temperature               | double precision  | °C   |             |            |
| min_snowmelt                        | double precision  | mm   |             |            |
| max_snowmelt                        | double precision  | mm   |             |            |
| mean_snowmelt                       | double precision  | mm   |             |            |
| min_soil_temperature_level_1        | double precision  | °C   |             |            |
| max_soil_temperature_level_1        | double precision  | °C   |             |            |
| mean_soil_temperature_level_1       | double precision  | °C   |             |            |
| min_soil_temperature_level_2        | double precision  | °C   |             |            |
| max_soil_temperature_level_2        | double precision  | °C   |             |            |
| mean_soil_temperature_level_2       | double precision  | °C   |             |            |
| min_soil_temperature_level_3        | double precision  | °C   |             |            |
| max_soil_temperature_level_3        | double precision  | °C   |             |            |
| mean_soil_temperature_level_3       | double precision  | °C   |             |            |
| min_soil_temperature_level_4        | double precision  | °C   |             |            |
| max_soil_temperature_level_4        | double precision  | °C   |             |            |
| mean_soil_temperature_level_4       | double precision  | °C   |             |            |
| min_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| max_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| mean_surface_net_solar_radiation    | double precision  | W/m² |             |            |
| min_surface_pressure                | double precision  | Pa   |             |            |
| max_surface_pressure                | double precision  | Pa   |             |            |
| mean_surface_pressure               | double precision  | Pa   |             |            |
| min_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_1  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_2  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_3  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_4  | double precision  | m³/m³|             |            |
| min_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| max_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| mean_leaf_area_index_high_vegetation| double precision  | -    |             |            |
| min_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| max_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| mean_leaf_area_index_low_vegetation | double precision  | -    |             |            |
| day_of_year                         | integer           | -    |             |            |
| month_y                             | double precision  | -    |             |            |
| day_y                               | double precision  | -    |             |            |
| soil_moisture_min                   | double precision  | m³/m³|             |            |
| soil_moisture_max                   | double precision  | m³/m³|             |            |
| soil_moisture_mean                  | double precision  | m³/m³|             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_weekly_sat_soil
- Schema: public
- Columns: 62

A table containing weekly aggregate weather data from the copernicus satellite dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_weekly_sat_soil attribute list</summary>

| Attribute                           | Type              | Unit | Description | Constraint |
| ----------------------------------- | ----------------- | ---- | ----------- | ---------- |
| year                                | bigint            | -    |             |            |
| month_x                             | bigint            | -    |             |            |
| week_of_year                        | bigint            | -    |             |            |
| district                            | bigint            | -    |             |            |
| min_dewpoint_temperature            | double precision  | °C   |             |            |
| max_dewpoint_temperature            | double precision  | °C   |             |            |
| mean_dewpoint_temperature           | double precision  | °C   |             |            |
| min_temperature                     | double precision  | °C   |             |            |
| max_temperature                     | double precision  | °C   |             |            |
| mean_temperature                    | double precision  | °C   |             |            |
| min_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| max_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| mean_evaporation_from_bare_soil     | double precision  | mm   |             |            |
| min_skin_reservoir_content          | double precision  | mm   |             |            |
| max_skin_reservoir_content          | double precision  | mm   |             |            |
| mean_skin_reservoir_content         | double precision  | mm   |             |            |
| min_skin_temperature                | double precision  | °C   |             |            |
| max_skin_temperature                | double precision  | °C   |             |            |
| mean_skin_temperature               | double precision  | °C   |             |            |
| min_snowmelt                        | double precision  | mm   |             |            |
| max_snowmelt                        | double precision  | mm   |             |            |
| mean_snowmelt                       | double precision  | mm   |             |            |
| min_soil_temperature_level_1        | double precision  | °C   |             |            |
| max_soil_temperature_level_1        | double precision  | °C   |             |            |
| mean_soil_temperature_level_1       | double precision  | °C   |             |            |
| min_soil_temperature_level_2        | double precision  | °C   |             |            |
| max_soil_temperature_level_2        | double precision  | °C   |             |            |
| mean_soil_temperature_level_2       | double precision  | °C   |             |            |
| min_soil_temperature_level_3        | double precision  | °C   |             |            |
| max_soil_temperature_level_3        | double precision  | °C   |             |            |
| mean_soil_temperature_level_3       | double precision  | °C   |             |            |
| min_soil_temperature_level_4        | double precision  | °C   |             |            |
| max_soil_temperature_level_4        | double precision  | °C   |             |            |
| mean_soil_temperature_level_4       | double precision  | °C   |             |            |
| min_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| max_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| mean_surface_net_solar_radiation    | double precision  | W/m² |             |            |
| min_surface_pressure                | double precision  | Pa   |             |            |
| max_surface_pressure                | double precision  | Pa   |             |            |
| mean_surface_pressure               | double precision  | Pa   |             |            |
| min_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_1  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_2  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_3  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_4  | double precision  | m³/m³|             |            |
| min_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| max_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| mean_leaf_area_index_high_vegetation| double precision  | -    |             |            |
| min_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| max_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| mean_leaf_area_index_low_vegetation | double precision  | -    |             |            |
| month_y                             | double precision  | -    |             |            |
| soil_moisture_min                   | double precision  | m³/m³|             |            |
| soil_moisture_max                   | double precision  | m³/m³|             |            |
| soil_moisture_mean                  | double precision  | m³/m³|             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_monthly_sat_soil
- Schema: public
- Columns: 60

A table containing monthly aggregate weather data from the copernicus satellite dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_monthly_sat_soil attribute list</summary>

| Attribute                           | Type              | Unit | Description | Constraint |
| ----------------------------------- | ----------------- | ---- | ----------- | ---------- |
| year                                | bigint            | -    |             |            |
| month                               | bigint            | -    |             |            |
| district                            | bigint            | -    |             |            |
| min_dewpoint_temperature            | double precision  | °C   |             |            |
| max_dewpoint_temperature            | double precision  | °C   |             |            |
| mean_dewpoint_temperature           | double precision  | °C   |             |            |
| min_temperature                     | double precision  | °C   |             |            |
| max_temperature                     | double precision  | °C   |             |            |
| mean_temperature                    | double precision  | °C   |             |            |
| min_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| max_evaporation_from_bare_soil      | double precision  | mm   |             |            |
| mean_evaporation_from_bare_soil     | double precision  | mm   |             |            |
| min_skin_reservoir_content          | double precision  | mm   |             |            |
| max_skin_reservoir_content          | double precision  | mm   |             |            |
| mean_skin_reservoir_content         | double precision  | mm   |             |            |
| min_skin_temperature                | double precision  | °C   |             |            |
| max_skin_temperature                | double precision  | °C   |             |            |
| mean_skin_temperature               | double precision  | °C   |             |            |
| min_snowmelt                        | double precision  | mm   |             |            |
| max_snowmelt                        | double precision  | mm   |             |            |
| mean_snowmelt                       | double precision  | mm   |             |            |
| min_soil_temperature_level_1        | double precision  | °C   |             |            |
| max_soil_temperature_level_1        | double precision  | °C   |             |            |
| mean_soil_temperature_level_1       | double precision  | °C   |             |            |
| min_soil_temperature_level_2        | double precision  | °C   |             |            |
| max_soil_temperature_level_2        | double precision  | °C   |             |            |
| mean_soil_temperature_level_2       | double precision  | °C   |             |            |
| min_soil_temperature_level_3        | double precision  | °C   |             |            |
| max_soil_temperature_level_3        | double precision  | °C   |             |            |
| mean_soil_temperature_level_3       | double precision  | °C   |             |            |
| min_soil_temperature_level_4        | double precision  | °C   |             |            |
| max_soil_temperature_level_4        | double precision  | °C   |             |            |
| mean_soil_temperature_level_4       | double precision  | °C   |             |            |
| min_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| max_surface_net_solar_radiation     | double precision  | W/m² |             |            |
| mean_surface_net_solar_radiation    | double precision  | W/m² |             |            |
| min_surface_pressure                | double precision  | Pa   |             |            |
| max_surface_pressure                | double precision  | Pa   |             |            |
| mean_surface_pressure               | double precision  | Pa   |             |            |
| min_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_1   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_1  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_2   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_2  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_3   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_3  | double precision  | m³/m³|             |            |
| min_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| max_volumetric_soil_water_layer_4   | double precision  | m³/m³|             |            |
| mean_volumetric_soil_water_layer_4  | double precision  | m³/m³|             |            |
| min_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| max_leaf_area_index_high_vegetation | double precision  | -    |             |            |
| mean_leaf_area_index_high_vegetation| double precision  | -    |             |            |
| min_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| max_leaf_area_index_low_vegetation  | double precision  | -    |             |            |
| mean_leaf_area_index_low_vegetation | double precision  | -    |             |            |
| soil_moisture_min                   | double precision  | m³/m³|             |            |
| soil_moisture_max                   | double precision  | m³/m³|             |            |
| soil_moisture_mean                  | double precision  | m³/m³|             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_daily_station_soil
- Schema: public
- Columns: 46

A table containing daily aggregate weather data from the weather station dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_daily_station_soil attribute list</summary>

| Attribute           | Type              | Unit      | Description | Constraint |
| ------------------- | ----------------- | --------- | ----------- | ---------- |
| district            | bigint            | -         |             |            |
| year                | bigint            | -         |             |            |
| month_x             | bigint            | -         |             |            |
| day_x               | bigint            | -         |             |            |
| min_temp_x          | double precision  | °C        |             |            |
| max_temp_x          | double precision  | °C        |             |            |
| mean_temp_x         | double precision  | °C        |             |            |
| min_dew_point_temp  | double precision  | °C        |             |            |
| max_dew_point_temp  | double precision  | °C        |             |            |
| mean_dew_point_temp | double precision  | °C        |             |            |
| min_humidex         | double precision  | -         |             |            |
| max_humidex         | double precision  | -         |             |            |
| mean_humidex        | double precision  | -         |             |            |
| min_precip          | double precision  | mm        |             |            |
| max_precip          | double precision  | mm        |             |            |
| mean_precip         | double precision  | mm        |             |            |
| min_rel_humid       | double precision  | %         |             |            |
| max_rel_humid       | double precision  | %         |             |            |
| mean_rel_humid      | double precision  | %         |             |            |
| min_stn_press       | double precision  | Pa        |             |            |
| max_stn_press       | double precision  | Pa        |             |            |
| mean_stn_press      | double precision  | Pa        |             |            |
| min_visibility      | double precision  | km        |             |            |
| max_visibility      | double precision  | km        |             |            |
| mean_visibility     | double precision  | km        |             |            |
| max_temp_y          | double precision  | °C        |             |            |
| min_temp_y          | double precision  | °C        |             |            |
| mean_temp_y         | double precision  | °C        |             |            |
| min_total_rain      | double precision  | mm        |             |            |
| max_total_rain      | double precision  | mm        |             |            |
| mean_total_rain     | double precision  | mm        |             |            |
| min_total_snow      | double precision  | cm        |             |            |
| max_total_snow      | double precision  | cm        |             |            |
| mean_total_snow     | double precision  | cm        |             |            |
| min_total_precip    | double precision  | mm        |             |            |
| max_total_precip    | double precision  | mm        |             |            |
| mean_total_precip   | double precision  | mm        |             |            |
| min_snow_on_grnd    | double precision  | cm        |             |            |
| max_snow_on_grnd    | double precision  | cm        |             |            |
| mean_snow_on_grnd   | double precision  | cm        |             |            |
| day_of_year         | integer           | -         |             |            |
| month_y             | double precision  | -         |             |            |
| day_y               | double precision  | -         |             |            |
| soil_moisture_min   | double precision  | m³/m³     |             |            |
| soil_moisture_max   | double precision  | m³/m³     |             |            |
| soil_moisture_mean  | double precision  | m³/m³     |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_weekly_station_soil
- Schema: public
- Columns: 44

A table containing weekly aggregate weather data from the weather station dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_weekly_station_soil attribute list</summary>

| Attribute           | Type              | Unit      | Description | Constraint |
| ------------------- | ----------------- | --------- | ----------- | ---------- |
| year                | bigint            | -         |             |            |
| month_x             | bigint            | -         |             |            |
| week_of_year        | bigint            | -         |             |            |
| district            | bigint            | -         |             |            |
| min_temp_x          | double precision  | °C        |             |            |
| max_temp_x          | double precision  | °C        |             |            |
| mean_temp_x         | double precision  | °C        |             |            |
| min_dew_point_temp  | double precision  | °C        |             |            |
| max_dew_point_temp  | double precision  | °C        |             |            |
| mean_dew_point_temp | double precision  | °C        |             |            |
| min_humidex         | double precision  | -         |             |            |
| max_humidex         | double precision  | -         |             |            |
| mean_humidex        | double precision  | -         |             |            |
| min_precip          | double precision  | mm        |             |            |
| max_precip          | double precision  | mm        |             |            |
| mean_precip         | double precision  | mm        |             |            |
| min_rel_humid       | double precision  | %         |             |            |
| max_rel_humid       | double precision  | %         |             |            |
| mean_rel_humid      | double precision  | %         |             |            |
| min_stn_press       | double precision  | Pa        |             |            |
| max_stn_press       | double precision  | Pa        |             |            |
| mean_stn_press      | double precision  | Pa        |             |            |
| min_visibility      | double precision  | km        |             |            |
| max_visibility      | double precision  | km        |             |            |
| mean_visibility     | double precision  | km        |             |            |
| max_temp_y          | double precision  | °C        |             |            |
| min_temp_y          | double precision  | °C        |             |            |
| mean_temp_y         | double precision  | °C        |             |            |
| min_total_rain      | double precision  | mm        |             |            |
| max_total_rain      | double precision  | mm        |             |            |
| mean_total_rain     | double precision  | mm        |             |            |
| min_total_snow      | double precision  | cm        |             |            |
| max_total_snow      | double precision  | cm        |             |            |
| mean_total_snow     | double precision  | cm        |             |            |
| min_total_precip    | double precision  | mm        |             |            |
| max_total_precip    | double precision  | mm        |             |            |
| mean_total_precip   | double precision  | mm        |             |            |
| min_snow_on_grnd    | double precision  | cm        |             |            |
| max_snow_on_grnd    | double precision  | cm        |             |            |
| mean_snow_on_grnd   | double precision  | cm        |             |            |
| month_y             | double precision  | -         |             |            |
| soil_moisture_min   | double precision  | m³/m³     |             |            |
| soil_moisture_max   | double precision  | m³/m³     |             |            |
| soil_moisture_mean  | double precision  | m³/m³     |             |            |

</details>

[back to top](#overview)
<br>
<br>

### dataset_monthly_station_soil
- Schema: public
- Columns: 42

A table containing monthly aggregate weather data from the weather station dataset joined with soil moisture data from the satellite dataset.
<details><summary>Vertical view dataset_monthly_station_soil attribute list</summary>

| Attribute           | Type              | Unit      | Description | Constraint |
| ------------------- | ----------------- | --------- | ----------- | ---------- |
| year                | bigint            | -         |             |            |
| month               | bigint            | -         |             |            |
| district            | bigint            | -         |             |            |
| min_temp_x          | double precision  | °C        |             |            |
| max_temp_x          | double precision  | °C        |             |            |
| mean_temp_x         | double precision  | °C        |             |            |
| min_dew_point_temp  | double precision  | °C        |             |            |
| max_dew_point_temp  | double precision  | °C        |             |            |
| mean_dew_point_temp | double precision  | °C        |             |            |
| min_humidex         | double precision  | -         |             |            |
| max_humidex         | double precision  | -         |             |            |
| mean_humidex        | double precision  | -         |             |            |
| min_precip          | double precision  | mm        |             |            |
| max_precip          | double precision  | mm        |             |            |
| mean_precip         | double precision  | mm        |             |            |
| min_rel_humid       | double precision  | %         |             |            |
| max_rel_humid       | double precision  | %         |             |            |
| mean_rel_humid      | double precision  | %         |             |            |
| min_stn_press       | double precision  | Pa        |             |            |
| max_stn_press       | double precision  | Pa        |             |            |
| mean_stn_press      | double precision  | Pa        |             |            |
| min_visibility      | double precision  | km        |             |            |
| max_visibility      | double precision  | km        |             |            |
| mean_visibility     | double precision  | km        |             |            |
| max_temp_y          | double precision  | °C        |             |            |
| min_temp_y          | double precision  | °C        |             |            |
| mean_temp_y         | double precision  | °C        |             |            |
| min_total_rain      | double precision  | mm        |             |            |
| max_total_rain      | double precision  | mm        |             |            |
| mean_total_rain     | double precision  | mm        |             |            |
| min_total_snow      | double precision  | cm        |             |            |
| max_total_snow      | double precision  | cm        |             |            |
| mean_total_snow     | double precision  | cm        |             |            |
| min_total_precip    | double precision  | mm        |             |            |
| max_total_precip    | double precision  | mm        |             |            |
| mean_total_precip   | double precision  | mm        |             |            |
| min_snow_on_grnd    | double precision  | cm        |             |            |
| max_snow_on_grnd    | double precision  | cm        |             |            |
| mean_snow_on_grnd   | double precision  | cm        |             |            |
| soil_moisture_min   | double precision  | m³/m³     |             |            |
| soil_moisture_max   | double precision  | m³/m³     |             |            |
| soil_moisture_mean  | double precision  | m³/m³     |             |            |

</details>

[back to top](#overview)
<br>
<br>

### copernicus_satelite_data
- Schema: public  
- Columns: 26

A european satellite that tracks many of earths environmental variables. Comprehensive data descriptions can be found [here](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview).  Please note that the naming scheme for all variables are kept consistant **with an exception of 2m_dewpoint_temperature and 2m_temperature** which due to SQL restrictions have been renamed as **dewpoint_temperature** and **temperature** respectively.


<details><summary>Vertical view copernicus_satellite_data attribute list</summary>

| attr                                  | type              | unit                  | desc                                      |
| ------------------------------------- | ----------------- | --------------------- | ----------------------------------------- |
| lon                                   | double            | EPSG:3347             | X coordinate (longitude)                  |
| lat                                   | double            | EPSG:3347             | Y coordinate (latitude)                   |
| datetime                              | timestamp         | YEAR-MO-DA HO:MN:SC   |                                           |
| year                                  | int               |                       |                                           |
| month                                 | int               |                       |                                           |
| day                                   | int               |                       |                                           |
| hour                                  | int               |                       |                                           |
| cr_num                                | int               |                       | identifies groups of related districts    |
| dewpoint_temperature                  | double            | K                     | labeled as 2m_dewpoint_temperature on copernicus |
| temperature                           | double            | K                     | labeled as 2m_temperature on copernicus  |
| evaporation_from_bare_soil            | double            | m of water equivalent |                                           |
| skin_reservoir_content                | double            | m of water equivalent |                                           |
| skin_temperature                      | double            | K                     |                                           |
| snowmelt                              | double            | m of water equivalent |                                           |
| soil_temperature_level_1              | double            | K                     |                                           |
| soil_temperature_level_2              | double            | K                     |                                           |
| soil_temperature_level_3              | double            | K                     |                                           |
| soil_temperature_level_4              | double            | K                     |                                           |
| surface_net_solar_radiation           | double            | Jm^-2                 |                                           |
| surface_pressure                      | double            | Pa                    |                                           |
| volumetric_soil_water_layer_1         | double            | m^3m^-3               |                                           |
| volumetric_soil_water_layer_2         | double            | m^3m^-3               |                                           |
| volumetric_soil_water_layer_3         | double            | m^3m^-3               |                                           |
| volumetric_soil_water_layer_4         | double            | m^3m^-3               |                                           |
| leaf_area_index_high_vegetation       | double            | m^2m^-2               |                                           |
| leaf_area_index_low_vegetation        | double            | m^2m^-2               |                                           |


</details>

<details><summary>Horizontal view copernicus_satellite_data attribute list</summary>
    

||lon|lat|datetime|year|month|day|hour|cr_num|dewpoint_temperature| temperature | evaporation_from_bare_soil | skin_reservoir_content  | skin_temperature | snowmelt | soil_temperature_level_1| soil_temperature_level_2| soil_temperature_level_3 | soil_temperature_level_4  | surface_net_solar_radiation | surface_pressure | volumetric_soil_water_layer_1 | volumetric_soil_water_layer_2  | volumetric_soil_water_layer_3  | volumetric_soil_water_layer_4 |leaf_area_index_high_vegetation|leaf_area_index_low_vegetation|
|-| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |------------- |------------- |------------- |-|-|-|-|-|-|-|
|**description**|X coordinate (longitude)|Y coordinate (latitude)||||||identifies groups of related districts|labeled as 2m_dewpoint_temperature on copernicus|labeled as 2m_temperature on copernicus|
|**type**|double|double|timestamp without time zone|int|int|int|int|int|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|
|**unit**|EPSG:3347|EPSG:3347|YEAR-MO-DA HO:MN:SC||||||K|K|m of water equivalent|m of water equivalent|K|m of water equivalent|K|K|K|K|Jm^-2|Pa|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^2m^-2|m^2m^-2|
|**constraints**|

</details>

[back to top](#overview)
<br>
<br>

### agg_day_copernicus_satellite_data
- Schema: public 
- Columns: 59

An aggregation of the mean, minimum and maximum values for the data found in the copernicus_satelite_data table per day. Similarly to the copernicus_satelite_data table, comprehensive data descriptions can be found [here](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview).


<details><summary>Vertical view agg_day_copernicus_satellite_data attribute list</summary>

| attr                                      | type              | unit                  | desc                                      |
| ----------------------------------------- | ----------------- | --------------------- | ----------------------------------------- |
| year                                      | int               |                       |                                           |
| month                                     | int               |                       |                                           |
| day                                       | int               |                       |                                           |
| cr_num                                    | int               |                       | identifies groups of related districts    |
| district                                  | double            |                       | unique region identifier                  |
| min_dewpoint_temperature                  | double            | K                     |                                           |
| max_dewpoint_temperature                  | double            | K                     |                                           |
| mean_dewpoint_temperature                 | double            | K                     |                                           |
| min_temperature                           | double            | K                     |                                           |
| max_temperature                           | double            | K                     |                                           |
| mean_temperature                          | double            | K                     |                                           |
| min_evaporation_from_bare_soil            | double            | m of water equivalent |                                           |
| max_evaporation_from_bare_soil            | double            | m of water equivalent |                                           |
| mean_evaporation_from_bare_soil           | double            | m of water equivalent |                                           |
| min_skin_reservoir_content                | double            | m of water equivalent |                                           |
| max_skin_reservoir_content                | double            | m of water equivalent |                                           |
| mean_skin_reservoir_content               | double            | m of water equivalent |                                           |
| min_skin_temperature                      | double            | K                     |                                           |
| max_skin_temperature                      | double            | K                     |                                           |
| mean_skin_temperature                     | double            | K                     |                                           |
| min_snowmelt                              | double            | m of water equivalent |                                           |
| max_snowmelt                              | double            | m of water equivalent |                                           |
| mean_snowmelt                             | double            | m of water equivalent |                                           |
| min_soil_temperature_level_1              | double            | K                     |                                           |
| max_soil_temperature_level_1              | double            | K                     |                                           |
| mean_soil_temperature_level_1             | double            | K                     |                                           |
| min_soil_temperature_level_2              | double            | K                     |                                           |
| max_soil_temperature_level_2              | double            | K                     |                                           |
| mean_soil_temperature_level_2             | double            | K                     |                                           |
| min_soil_temperature_level_3              | double            | K                     |                                           |
| max_soil_temperature_level_3              | double            | K                     |                                           |
| mean_soil_temperature_level_3             | double            | K                     |                                           |
| min_soil_temperature_level_4              | double            | K                     |                                           |
| max_soil_temperature_level_4              | double            | K                     |                                           |
| mean_soil_temperature_level_4             | double            | K                     |                                           |
| min_surface_net_solar_radiation           | double            | Jm^-2                 |                                           |
| max_surface_net_solar_radiation           | double            | Jm^-2                 |                                           |
| mean_surface_net_solar_radiation          | double            | Jm^-2                 |                                           |
| min_surface_pressure                      | double            | Pa                    |                                           |
| max_surface_pressure                      | double            | Pa                    |                                           |
| mean_surface_pressure                     | double            | Pa                    |                                           |
| min_volumetric_soil_water_layer_1         | double            | m^3m^-3               |                                           |
| max_volumetric_soil_water_layer_1         | double            | m^3m^-3               |                                           |
| mean_volumetric_soil_water_layer_1        | double            | m^3m^-3               |                                           |
| min_volumetric_soil_water_layer_2         | double            | m^3m^-3               |                                           |
| max_volumetric_soil_water_layer_2         | double            | m^3m^-3               |                                           |
| mean_volumetric_soil_water_layer_2        | double            | m^3m^-3               |                                           |
| min_volumetric_soil_water_layer_3         | double            | m^3m^-3               |                                           |
| max_volumetric_soil_water_layer_3         | double            | m^3m^-3               |                                           |
| mean_volumetric_soil_water_layer_3        | double            | m^3m^-3               |                                           |
| min_volumetric_soil_water_layer_4         | double            | m^3m^-3               |                                           |
| max_volumetric_soil_water_layer_4         | double            | m^3m^-3               |                                           |
| mean_volumetric_soil_water_layer_4        | double            | m^3m^-3               |                                           |
| min_leaf_area_index_high_vegetation       | double            | m^2m^-2               |                                           |
| max_leaf_area_index_high_vegetation       | double            | m^2m^-2               |                                           |
| mean_leaf_area_index_high_vegetation      | double            | m^2m^-2               |                                           |
| min_leaf_area_index_low_vegetation        | double            | m^2m^-2               |                                           |
| max_leaf_area_index_low_vegetation        | double            | m^2m^-2               |                                           |
| mean_leaf_area_index_low_vegetation       | double            | m^2m^-2               |                                           |


</details>

<details><summary>Horizontal view agg_day_copernicus_satellite_data attribute list</summary>
    

|year|month|day|cr_num|district|min_dewpoint_temperature|max_dewpoint_temperature|mean_dewpoint_temperature|min_temperature|max_temperature|mean_temperature|min_evaporation_from_bare_soil|max_evaporation_from_bare_soil|mean_evaporation_from_bare_soil|min_skin_reservoir_content|max_skin_reservoir_content|mean_skin_reservoir_content|min_skin_temperature|max_skin_temperature|mean_skin_temperature|min_snowmelt|max_snowmelt|mean_snowmelt|min_soil_temperature_level_1|max_soil_temperature_level_1|mean_soil_temperature_level_1|min_soil_temperature_level_2|max_soil_temperature_level_2|mean_soil_temperature_level_2|min_soil_temperature_level_3|max_soil_temperature_level_3|mean_soil_temperature_level_3|min_soil_temperature_level_4|max_soil_temperature_level_4|mean_soil_temperature_level_4|min_surface_net_solar_radiation|max_surface_net_solar_radiation|mean_surface_net_solar_radiation|min_surface_pressure|max_surface_pressure|mean_surface_pressure|min_volumetric_soil_water_layer_1|max_volumetric_soil_water_layer_1|mean_volumetric_soil_water_layer_1|min_volumetric_soil_water_layer_2|max_volumetric_soil_water_layer_2|mean_volumetric_soil_water_layer_2|min_volumetric_soil_water_layer_3|max_volumetric_soil_water_layer_3|mean_volumetric_soil_water_layer_3|min_volumetric_soil_water_layer_4|max_volumetric_soil_water_layer_4|mean_volumetric_soil_water_layer_4|min_leaf_area_index_high_vegetation|max_leaf_area_index_high_vegetation|mean_leaf_area_index_high_vegetation|min_leaf_area_index_low_vegetation|max_leaf_area_index_low_vegetation|mean_leaf_area_index_low_vegetation|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|||identifies groups of related districts|unique region identifier|
|**type**|int|int|int|int|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|
|**unit**|||||K|K|K|K|K|K|m of water equivalent|m of water equivalent|m of water equivalent|m of water equivalent|m of water equivalent|m of water equivalent|K|K|K|m of water equivalent|m of water equivalent|m of water equivalent|K|K|K|K|K|K|K|K|K|K|K|K|Jm^-2|Jm^-2|Jm^-2|Pa|Pa|Pa|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^3m^-3|m^2m^-2|m^2m^-2|m^2m^-2|m^2m^-2|m^2m^-2|m^2m^-2|
|**constraints**|

</details>

[back to top](#overview)
<br>
<br>

### ergot_sample
- Schema: public 
- Columns: 6

Contains all samples, both infected and diesease free, submited to the Canadian Harvest program by farmers to be tested for ergot. Of the original data, samples without a specified province and or district were discarded.

<details><summary>Vertical view ergot_sample attribute list</summary>

| attr           | type    | unit | description                                                   | constraints |
| -------------- | ------- | ---- | ------------------------------------------------------------- | ----------- |
| sample_id      | int     |      | unique sample identifier                                      | serial key  |
| year           | int     |      |                                                               |             |
| province       | string  |      | province abbreviation                                         |             |
| crop_district  | int     |      | non-unique identifier for a district within a province       |             |
| incidence      | boolean |      | truth value for the presence of ergot                         |             |
| severity       | double  | %    | percentage of severity detected                               |             |

</details>

<details><summary>Horizontal view ergot_sample attribute list</summary>
    

||sample_id|year|province|crop_district|incidence|severity|
|-|-|-|-|-|-|-|
|**description**|unique sample identifier||province abbreviation|non-unique identifier for a district within a province|truth value for the presence of ergot|percentage of severity detected|
|**type**|int|int|string|int|boolean|double|
|**unit**||||||%|
|**constraints**|serial key|

</details>


[back to top](#overview)
<br>
<br>

### ergot_sample_feat_eng
- Schema: public 
- Columns: 10

Similarly to the ergot_sample table, ergot_sample_feat_eng contains all samples, both infected and diesease free, submited to the Canadian Harvest program by farmers to be tested for ergot. Of the original data, samples without a specified province and or district were discarded. The data is enhanced with additional engineered features.

<details><summary>Vertical view ergot_sample_feat_eng attribute list</summary>

| attr               | type    | unit | description                                                                        | constraints |
| ------------------ | ------- | ---- | ---------------------------------------------------------------------------------- | ----------- |
| sample_id          | int     |      | unique sample identifier                                                           |             |
| year               | int     |      |                                                                                    |             |
| province           | string  |      | province abbreviation                                                              |             |
| crop_district      | int     |      | non-unique identifier for a district within a province                            |             |
| district           | int     |      | unique region identifier                                                           |             |
| incidence          | boolean |      | truth value for the presence of ergot                                              |             |
| severity           | double  |      | percentage of severity detected                                                    |             |
| downgrade          | boolean |      | comparison to ergot's selling threshold of 0.4%                                    |             |
| severity_bin_quan  | int     |      | severity binning on quantiles                                                      |             |
| severity_bin_arb   | int     |      | severity binning on 0.2, 0.4 and 0.8 respectively                                  |             |

</details>

<details><summary>Horizontal view ergot_sample_feat_eng attribute list</summary>
    

||sample_id|year|province|crop_district|district|incidence|severity|downgrade|severity_bin_quan|severity_bin_arb|
|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique sample identifier||province abbreviation|non-unique identifier for a district within a province|unique region identifier|truth value for the presence of ergot|percentage of severity detected|comparison to ergot's selling threshold of 0.4%|severity binning on quantiles|severity binning on 0.2, 0.4 and 0.8 respectively|
|**type**|int|int|string|int|int|boolean|double|boolean|int|int|
|**unit**|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### agg_ergot_sample
- Schema: public
- Columns: 32

An aggregation on the data found in the ergot_sample table per year and district.

<details><summary>Vertical view agg_ergot_sample attribute list</summary>

| attr                       | type    | unit | description                                                                        |
| -------------------------- | ------- | ---- | ---------------------------------------------------------------------------------- |
| year                       | int     |      |                                                                                    |
| district                   | int     |      | unique region identifier                                                           |
| percnt_true                | double  | %    | percentage of samples with ergot                                                   |
| has_ergot                  | boolean |      | district have any ergot?                                                           |
| median_severity            | double  |      |                                                                                    |
| sum_severity               | double  |      |                                                                                    |
| present_in_neighbor        | boolean |      |                                                                                    |
| sum_severity_in_neighbor   | double  |      |                                                                                    |
| present_prev1              | boolean |      | last year had ergot?                                                               |
| present_prev2              | boolean |      | 2 years ago had ergot? (non accumulative)                                          |
| present_prev3              | boolean |      | 3 years ago had ergot? (non accumulative)                                          |
| sum_severity_prev1         | double  |      | non accumulative                                                                   |
| sum_severity_prev2         | double  |      | non accumulative                                                                   |
| sum_severity_prev3         | double  |      | non accumulative                                                                   |
| percnt_true_prev1          | double  | %    | percentage of samples with ergot for the last year                                 |
| percnt_true_prev2          | double  | %    | percentage of samples with ergot 2 years ago (non accumulative)                    |
| percnt_true_prev3          | double  | %    | percentage of samples with ergot 3 years ago (non accumulative)                    |
| median_prev1               | double  |      | non accumulative                                                                   |
| median_prev2               | double  |      | non accumulative                                                                   |
| median_prev3               | double  |      | non accumulative                                                                   |
| sum_severity_prev1         | double  |      | non accumulative                                                                   |
| sum_severity_prev2         | double  |      | non accumulative                                                                   |
| sum_severity_prev3         | double  |      | non accumulative                                                                   |
| sum_severity_in_neighbor   | double  |      | non accumulative                                                                   |
| ergot_present_in_q1        | boolean |      | if the current (year, district) has its percnt_true in quantile 1                  |
| ergot_present_in_q2        | boolean |      | if the current (year, district) has its percnt_true in quantile 2                  |
| ergot_present_in_q3        | boolean |      | if the current (year, district) has its percnt_true in quantile 3                  |
| ergot_present_in_q4        | boolean |      | if the current (year, district) has its percnt_true in quantile 4                  |
| sum_severity_in_q1         | boolean |      | if the current (year, district) has its sum_severity in quantile 1                 |
| sum_severity_in_q2         | boolean |      | if the current (year, district) has its sum_severity in quantile 2                 |
| sum_severity_in_q3         | boolean |      | if the current (year, district) has its sum_severity in quantile 3                 |
| sum_severity_in_q4         | boolean |      | if the current (year, district) has its sum_severity in quantile 4                 |

</details>

<details><summary>Horizontal view agg_ergot_sample attribute list</summary>
    

||year|district|percnt_true|has_ergot|median_severity|sum_severity|present_in_neighbor|sum_severity_in_neighbor|present_prev1|present_prev2|present_prev3|sum_severity_prev1|sum_severity_prev2|sum_severity_prev3|percnt_true_prev1|percnt_true_prev2|percnt_true_prev3|median_prev1|median_prev2|median_prev3|sum_severity_prev1|sum_severity_prev2|sum_severity_prev3|sum_severity_in_neighbor|ergot_present_in_q1|ergot_present_in_q2|ergot_present_in_q3|ergot_present_in_q4|sum_severity_in_q1|sum_severity_in_q2|sum_severity_in_q3|sum_severity_in_q4|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**||unique region identifier|percentage of samples with ergot| district have any ergot?|||||last year had ergot?|2 years ago had ergot? (non accumulative)|3 years ago had ergot? (non accumulative)|non accumulative|non accumulative|non accumulative|percentage of samples with ergot for the last year|percentage of samples with ergot 2 years ago (non accumulative)|percentage of samples with ergot 3 years ago (non accumulative)|non accumulative|non accumulative|non accumulative|non accumulative|non accumulative|non accumulative|non accumulative|if the current (year, district) has its percnt_true in quantile 1|if the current (year, district) has its percnt_true in quantile 2|if the current (year, district) has its percnt_true in quantile 3|if the current (year, district) has its percnt_true in quantile 4|if the current (year, district) has its sum_severity in quantile 1|if the current (year, district) has its sum_severity in quantile 2|if the current (year, district) has its sum_severity in quantile 3|if the current (year, district) has its sum_severity in quantile 4|
|**type**|int|int|double|boolean|double|double|boolean|double|boolean|boolean|boolean|double|double|double|double|double|double|double|double|double|double|double|double|double|boolean|boolean|boolean|boolean|boolean|boolean|boolean|boolean|
|**unit**|||%||||||||||||%|%|%|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### agg_ergot_sample_v2
- Schema: public
- Columns: 0

Aggregation based on the downgrade threshold of 0.04 % ergot

<details><summary>Vertical view stations_dly attribute list</summary>

| |Description|Type|Unit|Constraints|
|-|----------|----|----|-----------|
|year||bigint||
|district||bigint||
|percnt_true||double precision|%|
|has_ergot||boolean||
|median_severity||double precision||
|sum_severity||double precision||
|present_in_neighbor||boolean||
|sum_severity_in_neighbor||double precision||
|present_prev1||boolean||
|present_prev2||boolean||
|present_prev3||boolean||
|sum_severity_prev1||double precision||
|sum_severity_prev2||double precision||
|sum_severity_prev3||double precision||
|percnt_true_prev1||double precision|%|
|percnt_true_prev2||double precision|%|
|percnt_true_prev3||double precision|%|
|median_prev1||double precision||
|median_prev2||double precision||
|median_prev3||double precision||
|severity_prev1||double precision||
|severity_prev2||double precision||
|severity_prev3||double precision||
|severity_in_neighbor||double precision||


</details>

<details><summary>Horizontal view stations_dly attribute list</summary>
    

</details>


[back to top](#overview)
<br>
<br>

### census_ag_regions
- Schema: public 
- Columns: 7

Holds the boundaries and geometries for provinces, districts and crop regions of interest.

<details><summary>Vertical view census_ag_regions attribute list</summary>

| attr      | type     | unit   | description                                                                 |
| --------- | -------- | ------ | --------------------------------------------------------------------------- |
| district  | int      |        | unique region identifier                                                    |
| car_name  | string   |        | region name                                                                 |
| pr_uid    | int      |        | province identifier                                                         |
| ag_uid    | string   |        |                                                                             |
| geometry  | geometry | binary | region geometry/boundaries                                                  |
| cr_num    | int      |        | identifies groups of related districts                                      |
| color     | string   | hex number  | assigned color on maps (based on cr_num)                                    |

</details>

<details><summary>Horizontal view census_ag_regions attribute list</summary>
    

||district|car_name|pr_uid|ag_uid|geometry|cr_num|color|
|-|-|-|-|-|-|-|-|
|**description**|unique region identifer|region name|province identifier| | region geometry/boundaries|identifies groups of related districts|assigned color on maps (based on cr_num)|
|**type**|int|string|int|string|geometry|int|string|
|**unit**|||||binary||hex number|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### labeled_soil
- Schema: public 
- Columns: 5

Initally our goal with this table was to deduce which soils appeared in which districts through their various geometries. However, due to the complexities of the soil data, our aggregation strategy changed making this table mostly obsolete. The picture below is a visualization of this, where each color represents a polygon which can contain as many as 21 different soil types.

<details><summary>Vertical view labeled_soil attribute list</summary>

| attr     | type   | unit | description                                                             |
| -------- | ------ | ---- | ----------------------------------------------------------------------- |
| id       | int    |      | unique row identifier                                                   |
| poly_id  | int    |      | unique geometry identifier                                              |
| soil_ids | string |      | ordered list of all unique soil ids found in geometry                   |
| cr_num   | double |      | identifies groups of related districts                                  |
| district | int    |      | unique region identifier                                                |

</details>

<details><summary>Horizontal view labeled_soil attribute list</summary>
    

||id|poly_id|soil_ids|cr_num|district|
|-|-|-|-|-|-|
|**description**|unique row identifier|unique geometry identifier|ordered list of all unique soil ids found in geometry|identifies groups of related districts|unique region identifer|
|**type**|int|int|string|double|int|
|**unit**|
|**constraints**|

</details>


<br>

<img src='.github/img/mappedSoils.png' width="600"/>

[back to top](#overview)
<br>
<br>

### soil_components
- Schema: public
- Columns: 15

Soil Components represent the divide of different soils found within their respective geometries (since there can be as many as 21 different soil types per geometry). Soil geometries do not necessairly match up with the geometries of the districts (from the census_ag_regions table), rather, **much like a geometry can have multiple soils, a district can have multiple components**. Comprehensive data descriptions can be found [here (components)](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/cmp/index.html) and [here (ratings)](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/crt/index.html). 

<details><summary>Vertical view soil_components attribute list</summary>

| attr              | type   | unit | description                                                                     |
| ----------------- | ------ | ---- | ------------------------------------------------------------------------------- |
| poly_id           | int    |      | unique geometry identifier                                                      |
| cmp               | int    |      | component identifer (each geometry can have multiple)                           |
| percent           | int    | %    | percentage of which a component fills its geometry                              |
| slope             | string |      | components                                                                      |
| stone             | string |      | components                                                                      |
| surface_area      | string |      | components                                                                      |
| province          | string |      | province abbreviation                                                           |
| soil_code         | string |      | components                                                                      |
| modifier          | string |      | defines soil characteristics (components)                                       |
| profile           | string |      | components                                                                      |
| soil_id           | string |      | components                                                                      |
| coarse_frag_1     | string |      | ratings                                                                         |
| coarse_frag_2     | string |      | ratings                                                                         |
| coarse_frag_3     | string |      | ratings                                                                         |
| depth             | string |      | ratings                                                                         |
| water_holding_cap | string |      | ratings                                                                         |

</details>

<details><summary>Horizontal view soil_components attribute list</summary>
    

||poly_id|cmp|percent|slope|stone|surface_area|province|soil_code|modifier|profile|soil_id|coarse_frag_1|coarse_frag_2|coarse_frag_3|depth|water_holding_cap|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique geometry identifier|component identifer (each geometry can have multiple)|percentage of which a component fills its geometry|(components)|(components)|(components)|province abbreviation|(components)|defines soil characteristics (components)|(components)|(components)|(ratings)|(ratings)|(ratings)|(ratings)|(ratings)
|**type**|int|int|int|string|string|string|string|string|string|string|string|string|string|string|string|string|
|**unit**||incrementing counter per poly_id|%|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### soil_data
- Schema: public 
- Columns: 47

The soil_data table holds the soil characteristics found in the different soils throughout a given province. Comprehensive data descriptions can be found [here (names)](https://sis.agr.gc.ca/cansis/nsdb/soil/v2/snt/index.html) and [here (layers)](https://sis.agr.gc.ca/cansis/nsdb/soil/v2/slt/index.html). 

<details><summary>Vertical view soil_data attribute list</summary>

| attr                        | type   | unit    | description                                           |
| --------------------------- | ------ | ------- | ----------------------------------------------------- |
| id                          | string |         | unique soil identifier                                |
| province                    | string |         | province abbreviation                                 |
| code                        | string |         |                                                       |
| modifier                    | string |         |                                                       |
| name                        | string |         | soil name (without abbreviations)                      |
| kind                        | string |         | kind of surface material (names)                       |
| water_table                 | string |         | (names)                                               |
| root_restrict               | string |         | (names)                                               |
| restr_type                  | string |         | (names)                                               |
| drainage                    | string |         | (names)                                               |
| parent_material_texture_1   | string |         | (names)                                               |
| parent_material_texture_2   | string |         | (names)                                               |
| parent_material_texture_3   | string |         | (names)                                               |
| parent_material_chemical_1  | string |         | (names)                                               |
| parent_material_chemical_2  | string |         | (names)                                               |
| parent_material_chemical_3  | string |         | (names)                                               |
| mode_of_depo_1              | string |         | (names)                                               |
| mode_of_depo_2              | string |         | (names)                                               |
| mode_of_depo_3              | string |         | (names)                                               |
| layer_no                    | int    |         | (layers)                                              |
| u_depth                     | int    | cm      | (layers)                                              |
| l_depth                     | int    | cm      | (layers)                                              |
| hzn_lit                     | string |         | (layers)                                              |
| hzn_mas                     | string |         | (layers)                                              |
| hzn_suf                     | string |         | (layers)                                              |
| hzn_mod                     | string |         | (layers)                                              |
| percnt_coarse_frag          | int    | %       | (layers)                                              |
| sand_texture                | string |         | (layers)                                              |
| percnt_v_fine_sand          | int    | %       | (layers)                                              |
| total_sand                  | int    | %       | (layers)                                              |
| total_silt                  | int    | %       | (layers)                                              |
| total_clay                  | int    | %       | (layers)                                              |
| percnt_carbon               | double | %       | (layers)                                              |
| calcium_ph                  | double | pH      | (layers)                                              |
| proj_ph                     | int    | pH      | (layers)                                              |
| percnt_base_sat             | double | %       | (layers)                                              |
| cec                         | int    | Meq/100g| (layers)                                              |
| ksat                        | int    | cm/h    | (layers)                                              |
| water_reten_0               | int    | %       | (layers)                                              |
| water_reten_10              | int    | %       | (layers)                                              |
| water_reten_33              | int    | %       | (layers)                                              |
| water_reten_1500            | int    | %       | (layers)                                              |
| bulk_density                | double | g/cm^3  | (layers)                                              |
| elec_cond                   | int    | dS/m    | (layers)                                              |
| calc_equiv                  | int    | %       | (layers)                                              |
| decomp_class                | int    |         | (layers)                                              |
| percnt_wood                 | int    | %       | (layers)                                              |

</details>

<details><summary>Horizontal view soil_data attribute list</summary>
    

||id|province|code|modifier|name|kind|water_table|root_restrict|restr_type|drainage|parent_material_texture_1|parent_material_texture_2|parent_material_texture_3|parent_material_chemical_1|parent_material_chemical_2|parent_material_chemical_3|mode_of_depo_1|mode_of_depo_2|mode_of_depo_3|layer_no|u_depth|l_depth|hzn_lit|hzn_mas|hzn_suf|hzn_mod|percnt_coarse_frag|sand_texture|percnt_v_fine_sand|total_sand|total_silt|total_clay|percnt_carbon|calcium_ph|proj_ph|percnt_base_sat|cec|ksat|water_reten_0|water_reten_10|water_reten_33|water_reten_1500|bulk_density|elec_cond|calc_equiv|decomp_class|percnt_wood|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique soil identifier|province abbreviation|||soil name (without abbreviations)|kind of surface material (names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(names)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|
|**type**|string|string|string|string|string|string|string|string|string|string|string|string|string|string|string|string|string|string|string|int|int|int|string|string|string|string|int|string|int|int|int|int|double|double|double|int|int|double|int|int|int|int|double|int|int|int|int|
|**unit**|||||||||||||||||||||cm|cm|||||%||%|%|%|%|%|pH|pH|%|Meq/100g|cm/h|%|%|%|%|g/cm^3|dS/m|%||%|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### soil_geometry
- Schema: public 
- Columns: 4

Holds the sizes and boundaries for the different soil geometries. Comprehensive data descriptions can be found [here](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/pat/index.html). 

<details><summary>Vertical view soil_geometry attribute list</summary>

| attr        | type    | unit     | description                |
| ----------- | ------- | -------- | -------------------------- |
| area        | double  |          |                            |
| perimeter   | double  |          |                            |
| poly_id     | int     |          | unique geometry identifier |
| geometry    | geometry| EPSG:3347|                            |

</details>

<details><summary>Horizontal view soil_geometry attribute list</summary>
    

||area|perimeter|poly_id|geometry|
|-|-|-|-|-|
|**description**|||unique geometry identifier||
|**type**|double|double|int|geometry|
|**unit**||||EPSG:3347|
|**constraints**|||||

</details>


[back to top](#overview)
<br>
<br>

### soil_surronding_land
- Schema: public 
- Columns: 6

The soil_surronding_land tables stores information about the land that surronds each soil geometry. Comprehensive data descriptions can be found [here](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/lat/index.html). 

<details><summary>Vertical view soil_surronding_land attribute list</summary>

| attr       | type | unit    | description                    |
| -----------| ---- | ------- | ------------------------------ |
| poly_id    | int  |         | unique geometry identifier     |
| land_area  | int  | hectares|                                |
| water_area | int  | hectares|                                |
| fresh_area | int  | hectares|                                |
| ocean_area | int  | hectares|                                |
| total_area | int  | hectares| accumulative                   |

</details>

<details><summary>Horizontal view soil_surronding_land attribute list</summary>
    

||poly_id|land_area|water_area|fresh_area|ocean_area|total_area|
|-|-|-|-|-|-|-|
|**description**|unique geometry identifier|||||accumulative|
|**type**|int|int|int|int|int|int|
|**unit**||hectares|hectares|hectares|hectares|hectares|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### agg_soil_data
- Schema: public
- Columns: 18

An aggregation on the mean values of the data found in the soil_data table per district. Note that all variables are weighted based on the percentage of the component they occupy. Comprehensive data descriptions can be found [here (layers)](https://sis.agr.gc.ca/cansis/nsdb/soil/v2/slt/index.html), 
[here (components)](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/cmp/index.html) and [here (surronding land)](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/lat/index.html).

<details><summary>Vertical view agg_soil_data attribute list</summary>

| attr                   | type   | unit     | description                        |
| ---------------------- | ------ | -------- | ---------------------------------- |
| district               | int    |          | unique region identifier           |
| avg_percnt_coarse_frag | double | %        | (layers)                           |
| avg_total_sand         | double | %        | (layers)                           |
| avg_total_silt         | double | %        | (layers)                           |
| avg_total_clay         | double | %        | (layers)                           |
| avg_percnt_carbon      | double | %        | (layers)                           |
| avg_calcium_ph         | double | ph       | (layers)                           |
| avg_proj_ph            | double | ph       | (layers)                           |
| avg_water_reten_0      | double | %        | (layers)                           |
| avg_water_reten_10     | double | %        | (layers)                           |
| avg_water_reten_33     | double | %        | (layers)                           |
| avg_water_reten_1500   | double | %        | (layers)                           |
| avg_bulk_density       | double | g/cm^3   | (layers)                           |
| avg_elec_cond          | double | dS/m     | (layers)                           |
| avg_percnt_wood        | double | %        | (layers)                           |
| avg_water_holding_cap  | double | %        | (components)                       |
| avg_land_area          | double | hectares | (surrounding land)                 |
| avg_water_area         | double | hectares | (surrounding land)                 |

</details>

<details><summary>Horizontal view agg_soil_data attribute list</summary>
    

||district|avg_percnt_coarse_frag|avg_total_sand|avg_total_silt|avg_total_clay|avg_percnt_carbon|avg_calcium_ph|avg_proj_ph|avg_water_reten_0|avg_water_reten_10|avg_water_reten_33|avg_water_reten_1500|avg_bulk_density|avg_elec_cond|avg_percnt_wood|avg_water_holding_cap|avg_land_area|avg_water_area|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique region identifier|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(layers)|(components)|(surronding land)|(surronding land)|
|**type**|int|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|
|**unit**||%|%|%|%|%|ph|ph|%|%|%|%|g/cm^3|dS/m|%|%|hectares|hectares|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### soil_moisture
- Schema: public 
- Columns: 7

Satellite soil moisture data.

<details><summary>Vertical view soil_moisture attribute list</summary>

| attr          | type   | unit           | description                       |
| ------------- | ------ | -------------- | --------------------------------- |
| id            | int    |                | unique recording identifier       |
| lon           | double | EPSG:3347      | X coordinate (longitude)          |
| lat           | double | EPSG:3347      | Y coordinate (latitude)           |
| date          | date   | YEAR-MO-DA     |                                   |
| cr_num        | int    |                | identifies groups of related districts |
| district      | int    |                | unique region identifier          |
| soil_moisture | double | <2cm thickness in % |                                |

</details>

<details><summary>Horizontal view soil_moisture attribute list</summary>
    

||id|lon|lat|date|cr_num|district|soil_moisture|
|-|-|-|-|-|-|-|-|
|**description**|unique recording identifier|X coordinate (longitude)|Y coordinate (latitude)||identifies groups of related districts|unique region identifier|
|**type**|int|double|double|date|int|int|double
|**unit**||EPSG:3347|EPSG:3347|YEAR-MO-DA|||<2cm thickness in %|
|**constraints**|key|

</details>


[back to top](#overview)
<br>
<br>

### agg_soil_moisture
- Schema: public 
- Columns: 9

An aggregation of the mean, minimum and maximum soil moisture values from the data found in the soil_moisture table per day and district.

<details><summary>Vertical view agg_soil_moisture attribute list</summary>

| attr               | type   | unit               | description                        |
| ------------------ | ------ | ------------------ | ---------------------------------- |
| index              | int    |                    | unique recording identifier        |
| year               | int    |                    |                                    |
| month              | int    |                    |                                    |
| day                | int    |                    |                                    |
| cr_num             | int    |                    | identifies groups of related districts  |
| district           | int    |                    | unique region identifier           |
| soil_moisture_min  | double | <2cm thickness in %|                                    |
| soil_moisture_max  | double | <2cm thickness in %|                                    |
| soil_moisture_mean | double | <2cm thickness in %|                                    |

</details>

<details><summary>Horizontal view agg_soil_moisture attribute list</summary>
    

||index|year|month|day|cr_num|district|soil_moisture_min|soil_moisture_max|soil_moisture_mean|
|-|-|-|-|-|-|-|-|-|-|
|**description**|unique recording identifier||||identifies groups of related districts|unique region identifier|
|**type**|int|int|int|int|int|int|double|double|double|
|**unit**|||||||<2cm thickness in %|<2cm thickness in %|<2cm thickness in %|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### ab_dly_station_data
### mb_dly_staion_data 
### sk_dly_station_data
- Schema: public 
- Columns: 12

The daily weather data from the various weather stations spread throughout Canada. Please note that **station_id is a string field**, this is because some stations contain letters in their unique identifier and that comprehensive documentation can be found [here](https://api.weather.gc.ca/openapi?f=html#/climate-daily/getClimate-dailyFeatures).

<details><summary>Vertical view sk_dly_station_data attribute list</summary>

| attr         | type                         | unit             | description                    |
| ------------ | ---------------------------- | ---------------- | ------------------------------ |
| station_id   | string                       |                  | unique station identifier      |
| date         | timestamp without time zone  | YEAR-MO-DA HO:MN:SC |                               |
| year         | int                          |                  |                               |
| month        | int                          |                  |                               |
| day          | int                          |                  |                               |
| max_temp     | double                       | °C               |                               |
| min_temp     | double                       | °C               |                               |
| mean_temp    | double                       | °C               |                               |
| total_rain   | double                       | mm               |                               |
| total_snow   | double                       | cm               |                               |
| total_precip | double                       | mm               |                               |
| snow_on_grnd | double                       | cm               |                               |

</details>

<details><summary>Horizontal view sk_dly_station_data attribute list</summary>
    

||station_id|date|year|month|day|max_temp|min_temp|mean_temp|total_rain|total_snow|total_precip|snow_on_grnd|
|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique station identifier||
|**type**|string|timestamp without time zone| int|int|int|double|double|double|double|double|double|double|
|**unit**||YEAR-MO-DA HO:MN:SC||||°C|°C|°C|mm|cm|mm|cm|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### ab_hly_station_data
### mb_hly_staion_data 
### sk_hly_station_data
- Schema: public 
- Columns: 24

The hourly weather data from the various weather stations spread throughout Canada. Please note that **station_id is a string field**, this is because some stations contain letters in their unique identifier and that comprehensive documentation can be found [here](https://api.weather.gc.ca/openapi?f=html#/climate-hourly/getClimate-hourlyFeatures).

<details><summary>Vertical view sk_hly_station_data attribute list</summary>

| attr                  | type    | unit  | description               |
|-----------------------|---------|-------|----------------------------|
| id                    | int     |       | unique row identifier     |
| station_id            | string  |       | unique station identifier |
| year                  | int     |       |                            |
| month                 | int     |       |                            |
| day                   | int     |       |                            |
| min_temp              | double  | °C    |                            |
| max_temp              | double  | °C    |                            |
| mean_temp             | double  | °C    |                            |
| min_dew_point_temp    | double  | °C    |                            |
| max_dew_point_temp    | double  | °C    |                            |
| mean_dew_point_temp   | double  | °C    |                            |
| min_humidex           | double  |       | how hot the weather feels |
| max_humidex           | double  |       | how hot the weather feels |
| mean_humidex          | double  |       | how hot the weather feels |
| total_precip          | double  | mm    |                            |
| min_rel_humid         | double  | %     |                            |
| max_rel_humid         | double  | %     |                            |
| mean_rel_humid        | double  | %     |                            |
| min_stn_press         | double  | kPa   | station pressure          |
| max_stn_press         | double  | kPa   | station pressure          |
| mean_stn_press        | double  | kPa   | station pressure          |
| min_visibility        | double  | km    |                            |
| max_visibility        | double  | km    |                            |
| mean_visibility       | double  | km    |                            |

</details>

<details><summary>Horizontal view sk_hly_station_data attribute list</summary>
    

||id|station_id|year|month|day|min_temp|max_temp|mean_temp|min_dew_point_temp|max_dew_point_temp|mean_dew_point_temp|min_humidex|max_humidex|mean_humidex|total_precip|min_rel_humid|max_rel_humid|mean_rel_humid|min_stn_press|max_stn_press|mean_stn_press|min_visibility|max_visibility|mean_visibility|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique row identifier|unique station identifier||||||||||how hot the weather feels|how hot the weather feels|how hot the weather feels|||||station pressure|station pressure|station pressure||||
|**type**|int|string|int|int|int|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|
|**unit**||||||°C|°C|°C|°C|°C|°C||||mm|%|%|%|kPa|kPa|kPa|km|km|km|
|**constraints**|key|

</details>


[back to top](#overview)
<br>
<br>

### agg_weather_combined
- Schema: public
- Columns: 40

Since our weather station data is split accross the hourly and daily tables and they share some attributes, agg_weather_combined was created to join the two. The data present is aggregated by minimum, maximum and mean values per district and day. Similiar to the daily and hourly stations, the hourly weather data from the various weather stations spread throughout Canada. Please note that **station_id is a string field**, this is because some stations contain letters in their unique identifier.

<details><summary>Vertical view agg_weather_combined list</summary>

| attr                 | type   | unit | description |
|----------------------|--------|------|-------------|
| district             | int    |      | unique region identifier |
| year                 | int    |      |             |
| month                | int    |      |             |
| day                  | int    |      |             |
| min_temp_x           | double | °C   | (hourly)    |
| max_temp_x           | double | °C   | (hourly)    |
| mean_temp_x          | double | °C   | (hourly)    |
| min_dew_point_temp   | double | °C   | (hourly)    |
| max_dew_point_temp   | double | °C   | (hourly)    |
| mean_dew_point_temp  | double | °C   | (hourly)    |
| min_humidex          | double |      | how hot the weather feels (hourly) |
| max_humidex          | double |      | how hot the weather feels (hourly) |
| mean_humidex         | double |      | how hot the weather feels (hourly) |
| min_precip           | double | mm   | (hourly)    |
| max_precip           | double | mm   | (hourly)    |
| mean_precip          | double | mm   | (hourly)    |
| min_rel_humid        | double | %    | (hourly)    |
| max_rel_humid        | double | %    | (hourly)    |
| mean_rel_humid       | double | %    | (hourly)    |
| min_stn_press        | double | kPa  | station pressure (hourly) |
| max_stn_press        | double | kPa  | station pressure (hourly) |
| mean_stn_press       | double | kPa  | station pressure (hourly) |
| min_visibility       | double | km   | (hourly)    |
| max_visibility       | double | km   | (hourly)    |
| mean_visibility      | double | km   | (hourly)    |
| max_temp_y           | double | °C   | (daily)     |
| min_temp_y           | double | °C   | (daily)     |
| mean_temp_y          | double | °C   | (daily)     |
| min_total_rain       | double | mm   | (daily)     |
| max_total_rain       | double | mm   | (daily)     |
| mean_total_rain      | double | mm   | (daily)     |
| min_total_snow       | double | cm   | (daily)     |
| max_total_snow       | double | cm   | (daily)     |
| mean_total_snow      | double | cm   | (daily)     |
| min_total_precip     | double | mm   | (daily)     |
| max_total_precip     | double | mm   | (daily)     |
| mean_total_precip    | double | mm   | (daily)     |
| min_snow_on_grnd     | double | cm   | (daily)     |
| max_snow_on_grnd     | double | cm   | (daily)     |
| mean_snow_on_grnd    | double | cm   | (daily)     |

</details>

<details><summary>Horizontal view agg_weather_combined attribute list</summary>
    

||district|year|month|day|min_temp_x|max_temp_x|mean_temp_x|min_dew_point_temp|max_dew_point_temp|mean_dew_point_temp|min_humidex|max_humidex|mean_humidex|min_precip|max_precip|mean_precip|min_rel_humid|max_rel_humid|mean_rel_humid|min_stn_press|max_stn_press|mean_stn_press|min_visibility|max_visibility|mean_visibility|max_temp_y|min_temp_y|mean_temp_y|min_total_rain|max_total_rain|mean_total_rain|min_total_snow|max_total_snow|mean_total_snow|min_total_precip|max_total_precip|mean_total_precip|min_snow_on_grnd|max_snow_on_grnd|mean_snow_on_grnd|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**|unique region identifier||||(hourly)|(hourly)|(hourly)|(hourly)|(hourly)|(hourly)|how hot the weather feels (hourly)|how hot the weather feels (hourly)|how hot the weather feels (hourly)|(hourly)|(hourly)|(hourly)|(hourly)|(hourly)|(hourly)|station pressure (hourly)|station pressure (hourly)|station pressure (hourly)|(hourly)|(hourly)|(hourly)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|(daily)|
|**type**|int|int|int|int|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|double|
|**unit**|||||°C|°C|°C|°C|°C|°C||||mm|mm|mm|%|%|%|kPa|kPa|kPa|km|km|km|°C|°C|°C|mm|mm|mm|cm|cm|cm|mm|mm|mm|cm|cm|cm|
|**constraints**|

</details>


[back to top](#overview)
<br>
<br>

### stations_dly
### stations_hly
- Schema: public 
- Columns: 20

The stations_dly and stations_hly tables contain meta data about the weather stations spread throughout Canada used to populate the weather station data tables. Please note that for **any set of coordinates, there may be one or more weather stations that may or may not be active** (depending on their first and last years). Furthermore, the **stated last years of a station do not reflect the absolute future use of a station**. Lastly, as per the image below, note that **daily stations appear in the same locations as hourly stations**.

<details><summary>Vertical view stations_hly attribute list</summary>

| attr                   | type     | unit       | description                                      |
|------------------------|----------|------------|--------------------------------------------------|
| station_name           | string   |            |                                                  |
| province               | string   |            | province abbreviation                            |
| latitude               | double   | EPSG:3347  | Y coordinate                                     |
| longitude              | double   | EPSG:3347  | X coordinate                                     |
| elevation              | double   | m          |                                                  |
| station_id             | string   |            | unique station identifier                        |
| wmo_identifier         | double   |            |                                                  |
| tc_identifer           | string   |            |                                                  |
| first_year             | int      |            | year of first records                            |
| last_year              | int      |            | year of last records                             |
| hly_first_year         | double   |            | year of first hourly records                     |
| hly_last_year          | double   |            | year of last hourly records                      |
| dly_first_year         | double   |            | year of first daily records                      |
| dly_last_year          | double   |            | year of last daily records                       |
| mly_first_year         | double   |            | year of first monthly records                    |
| mly_last_year          | double   |            | year of last monthly records                     |
| geometry               | geometry |            | weather station point                            |
| cr_num                 | double   |            | crop region number                               |
| district               | double   |            | unique region identifier                         |
| scraped                | boolean  |            | data been pulled? (**unused**)                   |

</details>

<details><summary>Horizontal view stations_hly attribute list</summary>
    

||station_name|province|latitude|longitude|elevation|station_id|wmo_identifier|tc_identifer|first_year|last_year|hly_first_year| hly_last_year|dly_first_year|dly_last_year|mly_first_year| mly_last_year|geometry|cr_num|district|scraped|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|**description**||province abbreviation|Y coordinate|X coordinate||unique station identifier|||year of first records|year of last records|year of first hourly records|yea of last hourly records|year of first daily records|year of last daily records|year of first monthly records| year of last monthly records|weather station point|crop region number|unique region identifier|data been pulled? (**unused**)|
|**type**|string|string|double|double|double|string|double|string|int|int|double|double|double|double|double|double|geometry|double|double|boolean|
|**unit**|||EPSG:3347|EPSG:3347|m|
|**constraints**|

</details>


<img src='.github/img/allStations.png' width="600"/>

[back to top](#overview)
<br>
<br>

### station_data_last_updated
- Schema: public 
- Columns: 3

This table is used to maintain the other weather station data tables using the dates they were last updated as well as by providing a manual override should a station become inactive or no longer disirable to have its information pulled.

<details><summary>Vertical view station_data_last_updated attribute list</summary>

| attr         | type     | unit       | description            |
|--------------|----------|------------|------------------------|
| station_id   | string   |            | unique station identifier |
| last_updated | date     | YEAR-MO-DA | latest data's date     |
| is_active    | boolean  |            | manual override        |

</details>

<details><summary>Horizontal view station_data_last_updated attribute list</summary>
    

||station_id|last_updated|is_active|
|-|-|-|-|
|**description**|unique station identifier|latest data's date|manual override|
|**type**|string|date|boolean|
|**unit**||YEAR-MO-DA|
|**constraints**|key|

</details>


[back to top](#overview)
<br>
<hr>
<br>

## Useful links:
- [Historical Weather Trends in Canada](https://climate.weather.gc.ca/index_e.html)
- [Agricultural Ecumene Boundary File - 2006](https://open.canada.ca/data/en/dataset/a3cc4d0a-34f8-4664-bb54-863427fb2243)
- [2006 Agricultural Ecumene Census Division Boundary Reference Guide](https://ftp.maps.canada.ca/pub/statcan_statcan/Agriculture_Agriculture/agricultural-ecumene-2006_ecoumene-agricole-2006/Agec2006RefGuide_EN.pdf)
- [Census Agricultural Regions Boundary Files of the 2006 Census of Agriculture](https://www150.statcan.gc.ca/n1/pub/92-174-x/92-174-x2007000-eng.htm)
- [Census Agricultural Regions 2006 Census of Agriculture Reference Guide](https://www150.statcan.gc.ca/pub/92-174-g/92-174-g2007000-eng.pdf)
- [Canadian Soil Landing Page](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/index.html)
- [Canadian Soil Entity Relationship Map](https://sis.agr.gc.ca/cansis/nsdb/slc/v3.2/model.html)
- [OAS Weather Station API Documentation](https://api.weather.gc.ca/openapi?f=html#/)


[back to top](#overview)
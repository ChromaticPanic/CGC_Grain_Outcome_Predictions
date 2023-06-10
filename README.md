<div align="center">
<h1>CGC Grain Outcome Predictions</h1>

<br>

<h4>Ergot is a plant disease that infects the developing grains of cereals and grasses. When ergot bodies instead of kernels emerge during kernel formation, ergot symptoms become visible. To find a strategy to prevent it sooner, it is crucial to identify the factors that encourage it to grow in grain. Our project aims to build a tool that supports this research and provides tools for data analysis for the Canadian Grain Commission.<h4>
</div>
<br>
<br>
<br>

## Overview
- [Data Sources](#data-sources)
- [Project Structure](#project-structure)
- [Setting up the environment](#setting-up-the-environment)
    - [Host Dependencies](#host-dependencies)
    - [PostgreSQL](#postgresql)
    - [PGADMIN -optional](#pgadmin)
    - [Tensorflow-gpu](#tensorflow-gpu)
    - [Tensorflow-cpu](#tensorflow-cpu)
    - [Customizing the Python Environment](#customizing-the-python-environment)
- [Accessing Jupyter Lab](#accessing-jupyter-lab)

<br>
<hr>
<br>

## Data Sources
- Provincial Boundaries
- Census Agricultural Regions
https://open.canada.ca/data/en/dataset/a3cc4d0a-34f8-4664-bb54-863427fb2243
https://ftp.maps.canada.ca/pub/statcan_statcan/Agriculture_Agriculture/agricultural-ecumene-2006_ecoumene-agricole-2006/Agec2006RefGuide_EN.pdf
https://www150.statcan.gc.ca/n1/pub/92-174-x/92-174-x2007000-eng.htm
https://www150.statcan.gc.ca/pub/92-174-g/92-174-g2007000-eng.pdf

mkdir src/WeatherStation/data/
cd src/WeatherStation/data/
wget https://www150.statcan.gc.ca/n1/pub/92-174-x/2007000/carboundary/gcar000b07a_e.zip


- Weather
https://climate.weather.gc.ca/index_e.html


- Weather Station Data
wget https://dd.weather.gc.ca/climate/observations/climate_station_list.csv

https://dd.weather.gc.ca/climate/observations/daily/
https://dd.weather.gc.ca/climate/observations/hourly/

- Satellite Land Moisture





## Project Structure
- stuff

## Setting up the environment
Our current environment is composed of docker containers housing PGADMIN4, PostgreSQL and the latest Ternsorflow Container with Jupyter Lab. On Linux the first step is to make a .env file from .env.local filling in the required variables with values you would like to use. On Windows you can use the setup.bat file to do this for you. The next step is to run the docker-compose command for the containers you would like to use. The following is a list of the containers and their respective commands. The commands should be run from the src/docker directory.  On windows, the setup.bat launches 3 containers: postgres, pgadmin, and tensorflow-cpu.  On linux, the containers can be launched using docker-compose --env-file=.env -f gpu-swarm.yaml up -d. The containers can also be launched individually via the individual yaml files.  For reference about common docker and docker-compose commands, see the Offcial Documentation.  

### Host Dependencies
[Tensorflow](https://www.tensorflow.org/install/docker)
- Windows
    - [Docker](https://www.docker.com/products/docker-desktop/)
    - [Docker Compose](https://docs.docker.com/compose/install/)
    - [Python](https://www.python.org/downloads/)
    - NVIDIA GPU Drivers (if using tensorflow-gpu) follow [official guide](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/running.html) guide for installation.
- Linux
    - [Docker](https://www.docker.com/products/docker-desktop/)
    - [Docker Compose](https://docs.docker.com/compose/install/)
    - [Python](https://www.python.org/downloads/)
    - NVIDIA GPU Drivers (if using tensorflow-gpu) follow [official guide](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/running.html) guide for installation.

### PGADMIN
- PGADMIN (optional) is a web-based interface for managing PostgreSQL databases. It is used to manage the database and can be accessed at http://localhost:5433. The default credentials are:
    - Email: xxxxxxxx
    - Password: xxxx

### PostgreSQL
- PostgreSQL is a relational database management system. It is used to store the data and can be accessed at http://localhost:5432. The default credentials are:
    - Username: xxxxxxxx
    - Password: xxxx
- cd src/docker
- sudo docker-compose --env-file=.env -f postgres.yaml up -d

### Tensorflow-gpu
- Tensorflow-gpu is a machine learning framework. It is used to train the model and can be accessed at http://localhost:8888. The default credentials are:
    - Token: xxxxxxxx
- sudo docker-compose -f tensorflow-gpu.yaml up -d
- sudo docker logs [container name] (to get token)

### Tensorflow-cpu
- Tensorflow-cpu is a machine learning framework. It is used to train the model and can be accessed at http://localhost:8888. The default credentials are:
    - Token: xxxxxxxx
- sudo docker-compose -f tensorflow-cpu.yaml up -d
- sudo docker logs [container name] (to get token)


To create/restart this environment use setup.bat from the project directory.

```setup.bat```

Additional steps are as follows:
- PGADMIN:
    1. refresh its respective webpage.
    2. enter credentials which can be found in ./config/.env and login.
    3. connect to postgres instance using the IP address: config-database-1, port: 5432 and the other credentials found in ./config/.env

<br>

- Jupyter notebooks:
    1. refresh its respective webpage and enter the token given from either the docker container terminal or CLI terminal. Alternatively, there will be a link you can press in both of these spots.
<br>

### Git-repo setup in linux
- Create a folder in the data folder using 'sudo mkdir maith'. Example: data/maith.
- Generate a personal access token for your git account (it's under Developer's settings).
- Run git clone 'https://<username>:<tokens>@github.com/ChromaticPanic/CGC_Grain_Outcome_Predictions.git' inside your personal folder.
    - **Note**: the username can be found in your email settings under the 'Keep my email addresses private'. Choose the one for performing web-based Git operations.

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

<br>
<hr>
<br>

## Data Sources
- Provincial Boundaries
- Census Agricultural Regions
- Weather Station List
- Weather Station Data

## Project Structure
- stuff

## Setting up the environment
Our current environment is composed of docker containers housing PGADMIN4, PostgreSQL and the latest Ternsorflow Container with Jupyter Lab.  

### Host Dependencies
[Tensorflow](https://www.tensorflow.org/install/docker)
- Windows
    - Docker
    - Docker Compose
    - Python [Python](https://www.python.org/downloads/)
    - NVIDIA GPU Drivers (if using tensorflow-gpu) follow [official guide](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/running.html) guide for installation.
- Linux
    - Docker
    - Docker Compose
    - Python [Python](https://www.python.org/downloads/)
    - NVIDIA GPU Drivers (if using tensorflow-gpu) follow [official guide](https://docs.nvidia.com/deeplearning/frameworks/tensorflow-release-notes/running.html) guide for installation.

### PGADMIN
- PGADMIN (optional) is a web-based interface for managing PostgreSQL databases. It is used to manage the database and can be accessed at http://localhost:5050. The default credentials are:
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

# Environment setup  
create a folder for the repo, cd into it  
``` bash  
git clone https://github.com/ChromaticPanic/MLweatherForestFire.git  
cd MLweatherForestFire/Docker  
touch data/.env  
nano data/.env  
```  
copy paste env file contents into file  
  
ctrl + o  
ctrl + x  
  
can either go through some weird complicated way to place data into WSL2 environment if on Windows or simply wait until the jupyterlab environment is setup and transfer files through the browser interface

# Jupyter Lab environment based on official tensorflow-gpu latest image  
  
Steps  
  
``` bash  
cd to the location of this readme  
```  
  
## Use if you have an NVIDIA GPU
``` bash  
sudo docker pull tensorflow/tensorflow:latest-gpu  
sudo docker build -f jupyter/gpuDockerfile -t tf-jupyter-lab .  
```  
  
## Use for cpu only
``` bash  
sudo docker pull tensorflow/tensorflow:latest  
sudo docker build -f jupyter/cpuDockerfile -t tf-jupyter-lab .  
```  
  
## to launch a container
``` bash  
sudo docker run -it --gpus all -p 14532:14532 -v data:/tf tf-jupyter-lab  
```  
  
# access jupyter lab through browser localhost:14532   
copy paste token from terminal  



# db swarm  
## postgres
``` bash  
sudo docker pull postgres  
sudo docker build -f postgres/Dockerfile -t postgresgis .  
```  

## PGAdmin  
``` bash  
sudo docker pull dpage/pgadmin4  
```  

## Start db swarm
``` bash  
sudo docker-compose -f docker-swarm.yaml -p "db-swarm" --env-file data/.env up -d  
```  

# access pgAdmin through localhost:15433

activate postgis via menu -> query tool and run
``` bash  
//Enable PostGIS (as of 3.0 contains just geometry/geography)
CREATE EXTENSION postgis;

//enable raster support (for 3+)
CREATE EXTENSION postgis_raster;

//Enable Topology
CREATE EXTENSION postgis_topology;
```
[Post Gis Site](https://postgis.net/install/#binary-installers)
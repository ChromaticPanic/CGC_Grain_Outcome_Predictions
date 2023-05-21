#Jupyter Lab environment based on official tensorflow-gpu latest image  
Steps  
``` bash
sudo docker pull tensorflow/tensorflow:latest-gpu  
sudo docker build -f Dockerfile -t tf-jupyter-lab .  
sudo docker run -it --gpus all -p 14532:14532 tf-jupyter-lab  
```  
access env through browser localhost:14532   
copy paste token from terminal  

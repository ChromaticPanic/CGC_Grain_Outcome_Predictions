FROM tensorflow/tensorflow:latest-gpu-jupyter
WORKDIR /tensorflow

RUN apt update && apt upgrade -y
RUN apt install -y screen

RUN /usr/bin/python3 -m pip install --upgrade pip
COPY ["requirements.txt", "/tensorflow/"]

RUN apt update && apt upgrade -y
RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD ["jupyter", "lab", "--port=8888", "--notebook-dir=/data", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
EXPOSE 8888

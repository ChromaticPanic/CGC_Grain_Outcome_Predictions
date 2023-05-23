FROM tensorflow/tensorflow:latest-jupyter
WORKDIR /tensorflow

RUN apt update && apt upgrade -y

RUN /usr/bin/python3 -m pip install --upgrade pip
COPY ["requirements.txt", "/tensorflow/"]

RUN pip install -r requirements.txt
RUN rm requirements.txt

CMD ["jupyter", "lab", "--port=8888", "--notebook-dir=/data", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
EXPOSE 8888

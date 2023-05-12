FROM postgres:latest
RUN apt update && apt upgrade
RUN apt install -y postgis
RUN mkdir -p /data/ && chmod -R a+rwx /data/
WORKDIR /data
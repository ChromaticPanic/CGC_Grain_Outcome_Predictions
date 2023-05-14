FROM postgres:latest

RUN apt update && apt upgrade
RUN apt install -y postgis

ADD init.sql /docker-entrypoint-initdb.d/
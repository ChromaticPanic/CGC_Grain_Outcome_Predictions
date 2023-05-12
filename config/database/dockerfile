FROM postgres:14

RUN apt-get update
RUN apt-get -y install postgresql-plpython3-14

ENV POSTGRES_DB=MOB
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password

ADD createDB.sql /docker-entrypoint-initdb.d/
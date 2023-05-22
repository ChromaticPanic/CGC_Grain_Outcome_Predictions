@echo off

REM preemptively connects to where the docker containers will be accessible
echo Please see docker or CLI for Jypiter token and .env for both the PGAdmin and database credentials
start "" http://localhost:8888
start "" http://localhost:5433

REM launches docker compose
echo Deploying docker containers!
set rootDir=%cd%
cd %rootDir%\src\docker
"docker" "compose" "up"
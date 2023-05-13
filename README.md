<div align="center">
<h1>CGC Grain Outcome Predictions</h1>

<br>

<h4>Ergot is a plant disease that infects the developing grains of cereals and grasses. When ergot bodies instead of kernels emerge during kernel formation, ergot symptoms become visible. To find a strategy to prevent it sooner, it is crucial to identify the factors that encourage it to grow in grain. Our project aims to build a tool that supports this research and provides tools for data analysis for the Canadian Grain Commission.<h4>
</div>
<br>
<br>
<br>

## Overview
- [Setting up the environment](#setting-up-the-environment)

<br>
<hr>
<br>

## Setting up the environment
Our current environment is composed of docker containers housing PGADMIN4, PostgreSQL and Jupyter notebook. To create/restart this environment use setup.bat from the project directory.

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

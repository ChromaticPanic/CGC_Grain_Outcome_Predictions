FROM tensorflow/tensorflow:latest-jupyter
WORKDIR /tensorflow

RUN /usr/bin/python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir jupyterlab matplotlib ipyparallel pandas numpy geopandas psycopg2-binary sqlalchemy scikit-learn pygeos rtree shapely seaborn python-dotenv

CMD ["jupyter", "lab", "--port=8888", "--notebook-dir=/data", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
EXPOSE 8888

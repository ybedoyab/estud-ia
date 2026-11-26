FROM apache/airflow:3.4.0

USER airflow
# La imagen ya trae estas versiones. Bajarlas choca con los proveedores incluidos.
RUN pip install --no-cache-dir "pandas==3.1.0" "requests==2.34.2"

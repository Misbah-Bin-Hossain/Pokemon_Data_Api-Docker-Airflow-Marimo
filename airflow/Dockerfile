# Dockerfile for the Airflow image used to run the ETL DAGs
# - Installs minimal system tools
# - Installs Python dependencies from requirements.txt
FROM apache/airflow:2.8.0

# Switch to root to install system deps
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

COPY requirements.txt /opt/airflow/requirements.txt

RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

ENV PYTHONPATH=/opt/airflow


# Dockerfile for Python ETL and Marimo notebook service
# Sets up a venv, installs core libs, and launches Marimo UI on port 8888
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y build-essential

# Copy requirements (if you have one)
COPY requirements.txt .

# Create venv, activate, and install requirements
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install pandas marimo

# Copy your notebooks (optional)
COPY notebooks/ /app/notebooks/

# Expose Marimo port
EXPOSE 8888

# Start Marimo automatically
CMD ["/bin/bash", "-c", ". .venv/bin/activate && python -m marimo edit --host 0.0.0.0 --port 8888"]
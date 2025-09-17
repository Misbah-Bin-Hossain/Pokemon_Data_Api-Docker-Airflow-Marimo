"""
Airflow DAG definition for the Pokémon ETL pipeline.
Defines four tasks which each fetch and load a resource type
into Postgres: pokemon, items, moves, and generations.
"""

# (Add your DAG/task code here or import from etl.py)
# If this file is intentionally minimal, you can use it to register the DAG from etl.py

# Example:
# from .etl import dag

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from etl import (
    fetch_pokemon,
    fetch_items,
    fetch_moves,
    fetch_generations,
    load_to_postgres,
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    'etl_pipeline',
    default_args=default_args,
    schedule_interval='@daily',  # run daily; adjust as needed
    catchup=False,  # don't backfill past dates
) as dag:

    # Extract + Load Pokémon master data
    pokemon_task = PythonOperator(
        task_id='load_pokemon',
        python_callable=lambda: load_to_postgres("pokemon", fetch_pokemon(limit=10000))
    )

    # Extract + Load item metadata
    items_task = PythonOperator(
        task_id='load_items',
        python_callable=lambda: load_to_postgres("items", fetch_items(limit=10000))
    )

    # Extract + Load move definitions and attributes
    moves_task = PythonOperator(
        task_id='load_moves',
        python_callable=lambda: load_to_postgres("moves", fetch_moves(limit=10000))
    )

    # Extract + Load generation groupings
    gens_task = PythonOperator(
        task_id='load_generations',
        python_callable=lambda: load_to_postgres("generations", fetch_generations(limit=10000))
    )

    # Simple linear dependency chain
    pokemon_task >> items_task >> moves_task >> gens_task

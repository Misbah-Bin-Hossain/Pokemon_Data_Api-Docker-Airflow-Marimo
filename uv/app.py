from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuration for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('postgresql+psycopg2://user:password@postgres:5432/pokemon_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/run_etl', methods=['POST'])
def run_etl():
    # Logic to trigger the ETL process
    # This could involve calling the ETL script or triggering a DAG in Airflow
    return "ETL process started", 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
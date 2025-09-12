# 🎯 Pokémon ETL Pipeline with Airflow, Postgres, and Marimo

Welcome to my **end-to-end ETL project** where I fetch data from the public [PokéAPI](https://pokeapi.co/), process it, and store it in a **Postgres database**.  
I orchestrate the pipeline with **Apache Airflow**, visualize and explore with **Marimo notebooks**, and manage everything using **Docker Compose**.  

---

## 🛠️ Tools I Used & Why

- **🐘 Postgres** → to persist Pokémon data (and keep it even if containers stop).  
- **🌬️ Apache Airflow** → to orchestrate ETL tasks (Extract → Transform → Load) with scheduling and monitoring.  
- **📦 Docker Compose** → to run multiple services (Airflow, Postgres, UV/Marimo) together in isolated containers.  
- **🧩 Marimo (in UV container)** → interactive notebook environment to query Postgres, test ETL queries, and visualize results.  
- **🐍 Python** → for the ETL scripts (using `requests`, `psycopg2`, `pandas`).

---

## 📂 Project Structure

```bash
.
├── airflow/                  # Airflow setup
│   ├── Dockerfile
│   ├── dags/                 # DAGs live here
│   │   └── etl_pipeline.py
│   └── requirements.txt
├── postgres/                 # Postgres setup
│   └── init.sql              # Schema creation
├── uv/                       # Marimo / Notebook container
│   ├── Dockerfile
│   ├── requirements.txt
│   └── (optional app.py if API trigger is needed)
├── docker-compose.yml         # Orchestrates all services
├── pyproject.toml             # Python project dependencies
└── README.md
```

---

## 🚀 How to Run

### 1. Clone this repo
```bash
git clone https://github.com/<your-username>/etl-pipeline-project.git
cd etl-pipeline-project
```

### 2. Start services with Docker Compose
```bash
docker compose up --build
```

This will start:  
- `postgres` → database  
- `airflow-webserver` → Airflow UI at [http://localhost:8080](http://localhost:8080)  
- `airflow-scheduler` → runs DAGs  
- `uv` → Marimo notebooks at [http://localhost:5000](http://localhost:5000)  

### 3. Initialize Airflow
Since Airflow needs DB setup and a user:
```bash
docker compose run airflow-init
```

Then restart Airflow:
```bash
docker compose restart airflow-webserver airflow-scheduler
```

✅ Login with:
- username: `admin`
- password: `admin`

### 4. Access Marimo
Go to [http://localhost:5000](http://localhost:5000) to open Marimo and query Postgres interactively.

---

## 📊 Database Schema

Tables created in Postgres (`init.sql`):

```sql
CREATE TABLE IF NOT EXISTS pokemon (
    id INT PRIMARY KEY,
    name TEXT,
    height INT,
    weight INT,
    base_experience INT,
    types TEXT[],
    abilities TEXT[],
    moves TEXT[],
    stats JSONB
);

CREATE TABLE IF NOT EXISTS items (
    id INT PRIMARY KEY,
    name TEXT,
    cost INT,
    category TEXT,
    effect TEXT
);

CREATE TABLE IF NOT EXISTS moves (
    id INT PRIMARY KEY,
    name TEXT,
    power INT,
    pp INT,
    accuracy INT,
    type TEXT,
    damage_class TEXT
);

CREATE TABLE IF NOT EXISTS generations (
    id INT PRIMARY KEY,
    name TEXT,
    main_region TEXT,
    pokemon_species TEXT[],
    moves TEXT[]
);
```

---

## 🔄 The ETL Flow

1. **Extract** → fetch data from PokéAPI  
2. **Transform** → clean/reshape into structured dicts  
3. **Load** → insert into Postgres (using `psycopg2`)  

In Airflow (`etl_pipeline.py`):
```python
extract_task >> transform_task >> load_task
```

In code (`main.py`):
```python
pokemon_data = fetch_pokemon(limit=50)
load_to_postgres(pokemon_data)
```

---

## 🧪 Exploring with Marimo

Inside Marimo notebooks:
```python
import pandas as pd
import psycopg2

conn = psycopg2.connect("dbname=pokemon_db user=user password=password host=postgres port=5432")

df = pd.read_sql("SELECT * FROM pokemon LIMIT 10;", conn)
df.head()
```

✅ This lets you run **SQL directly against Postgres** and visualize results interactively.

---

## ⚡ Problems I Faced & Solutions

### 1. ❌ Airflow DAGs not showing up
- **Cause:** I put `airflow db init && airflow users create` inside `docker-compose` commands. Airflow services were racing to start before DB was ready.  
- **Fix:** Moved DB init + user creation into a **separate `airflow-init` service**, ran it once before starting Airflow.

---

### 2. ❌ Arrays failing to insert in Postgres
```error
psycopg2.errors.InvalidTextRepresentation: malformed array literal
```
- **Cause:** I was trying to insert `['grass','poison']` as "grass,poison" instead of a Postgres array.  
- **Fix:** Passed Python lists directly (`types TEXT[]`) and serialized dicts with `json.dumps`.

---

### 3. ❌ Marimo notebooks lost after container stop
- **Cause:** No **volume** mounted in `uv` service.  
- **Fix:** Added a volume so notebooks persist:
```yaml
uv:
  volumes:
    - ./notebooks:/app/notebooks
```

---

### 4. ❌ Dependency conflicts (Uvicorn vs Marimo)
- **Cause:** `uvicorn==0.15.0` in requirements conflicted with Marimo needing `uvicorn>=0.22.0`.  
- **Fix:** Removed the pinned old version and let pip resolve the latest.

---

### 5. ❌ Airflow DAG duplicated ETL code
- **Cause:** Had `main.py` both inside `python/etl` and `airflow/dags`.  
- **Fix:** Mounted the ETL folder into Airflow, imported functions instead of duplicating code.

---

## 🧭 Lessons Learned

- Separate **ETL logic** (in Python) from **orchestration** (Airflow).  
- Always use **volumes** if you want persistence (Postgres data, notebooks, dags).  
- Docker Compose makes multi-container workflows much easier.  
- Airflow is powerful but requires careful initialization (DB + user).  
- Marimo is a great lightweight notebook alternative for quick SQL + data exploration.

---

## ✅ Next Steps

- Add CI/CD for running ETL tests before deployment.  
- Expand database schema (abilities, trainers, etc.).  
- Use Airflow connections instead of hardcoded credentials.  
- Add visualization dashboards.

---

## 🖥️ Demo

- **Airflow UI:** [http://localhost:8080](http://localhost:8080)  
- **Marimo Notebook:** [http://localhost:5000](http://localhost:5000)  
<img width="888" height="991" alt="image" src="https://github.com/user-attachments/assets/57a2ccc9-c5d1-48a9-9a87-4cd9a60afc0b" />

---
image.png

## 🤝 Contributing

Pull requests welcome! If you’d like to add new DAGs, expand schema, or improve docs, feel free.

---

## 📜 License
MIT License.

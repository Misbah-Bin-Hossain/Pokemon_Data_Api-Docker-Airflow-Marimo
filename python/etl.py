"""
ETL script for fetching Pokémon data from PokéAPI and loading it into Postgres.
Includes functions to fetch Pokémon, items, moves, generations, and load them into the database.
"""

import requests
import psycopg2
import time
import json

# Base URL for PokéAPI
BASE_URL = "https://pokeapi.co/api/v2"
# Default limit for API requests (set to None to fetch all data)
LIMIT = 10000  # change to None for all data

def fetch_data(endpoint, limit=LIMIT):
    """
    Fetch a list of resources from a given PokéAPI endpoint.
    Args:
        endpoint (str): API endpoint (e.g., 'pokemon', 'item').
        limit (int): Number of records to fetch.
    Returns:
        list: List of resource dicts with 'name' and 'url'.
    """
    url = f"{BASE_URL}/{endpoint}"
    if limit:
        url += f"?limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]

def fetch_detail(url):
    """
    Fetch detailed data for a single resource from its URL.
    Args:
        url (str): Resource URL.
    Returns:
        dict: Detailed resource data.
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_pokemon(limit=LIMIT):
    """
    Fetch detailed Pokémon data from PokéAPI.
    Args:
        limit (int): Number of Pokémon to fetch.
    Returns:
        list: List of Pokémon data dicts.
    """
    pokemon_list = fetch_data("pokemon", limit)
    data = []
    for idx, p in enumerate(pokemon_list, start=1):
        poke = fetch_detail(p["url"])
        data.append({
            "id": poke["id"],
            "name": poke["name"],
            "height": poke["height"],
            "weight": poke["weight"],
            "base_experience": poke.get("base_experience"),
            "types": [t["type"]["name"] for t in poke["types"]],
            "abilities": [a["ability"]["name"] for a in poke["abilities"]],
            "moves": [m["move"]["name"] for m in poke["moves"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
        })
        if idx % 10 == 0:
            print(f"Processed {idx} Pokémon...")
            time.sleep(0.5)  # Throttle requests to avoid rate limits
    return data

def fetch_items(limit=LIMIT):
    """
    Fetch detailed item data from PokéAPI.
    Args:
        limit (int): Number of items to fetch.
    Returns:
        list: List of item data dicts.
    """
    item_list = fetch_data("item", limit)
    data = []
    for i in item_list:
        item = fetch_detail(i["url"])
        data.append({
            "id": item["id"],
            "name": item["name"],
            "cost": item.get("cost"),
            "category": item["category"]["name"] if "category" in item else None,
            "effect": item["effect_entries"][0]["effect"] if item.get("effect_entries") else None
        })
    return data

def fetch_moves(limit=LIMIT):
    """
    Fetch detailed move data from PokéAPI.
    Args:
        limit (int): Number of moves to fetch.
    Returns:
        list: List of move data dicts.
    """
    move_list = fetch_data("move", limit)
    data = []
    for m in move_list:
        move = fetch_detail(m["url"])
        data.append({
            "id": move["id"],
            "name": move["name"],
            "power": move.get("power"),
            "pp": move.get("pp"),
            "accuracy": move.get("accuracy"),
            "type": move["type"]["name"] if "type" in move else None,
            "damage_class": move["damage_class"]["name"] if "damage_class" in move else None
        })
    return data

def fetch_generations(limit=LIMIT):
    """
    Fetch detailed generation data from PokéAPI.
    Args:
        limit (int): Number of generations to fetch.
    Returns:
        list: List of generation data dicts.
    """
    gen_list = fetch_data("generation", limit)
    data = []
    for g in gen_list:
        gen = fetch_detail(g["url"])
        data.append({
            "id": gen["id"],
            "name": gen["name"],
            "main_region": gen["main_region"]["name"] if "main_region" in gen else None,
            "pokemon_species": [s["name"] for s in gen["pokemon_species"]],
            "moves": [m["name"] for m in gen["moves"]],
        })
    return data

def load_to_postgres(table, records):
    """
    Load records into the specified Postgres table.
    Args:
        table (str): Table name ('pokemon', 'items', 'moves', 'generations').
        records (list): List of dicts to insert.
    """
    conn = psycopg2.connect(
        dbname="pokemon_db",
        user="user",
        password="password",
        host="postgres",
        port=5432
    )
    cur = conn.cursor()

    if table == "pokemon":
        for r in records:
            # Insert Pokémon data, serialize stats as JSON
            cur.execute("""
                INSERT INTO pokemon (id, name, height, weight, base_experience, types, abilities, moves, stats)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (r["id"], r["name"], r["height"], r["weight"], r["base_experience"],
                  r["types"], r["abilities"], r["moves"], json.dumps(r["stats"])))

    elif table == "items":
        for r in records:
            cur.execute("""
                INSERT INTO items (id, name, cost, category, effect)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (r["id"], r["name"], r["cost"], r["category"], r["effect"]))

    elif table == "moves":
        for r in records:
            cur.execute("""
                INSERT INTO moves (id, name, power, pp, accuracy, type, damage_class)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (r["id"], r["name"], r["power"], r["pp"], r["accuracy"], r["type"], r["damage_class"]))

    elif table == "generations":
        for r in records:
            cur.execute("""
                INSERT INTO generations (id, name, main_region, pokemon_species, moves)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO NOTHING
            """, (r["id"], r["name"], r["main_region"], r["pokemon_species"], r["moves"]))

    conn.commit()
    cur.close()
    conn.close()

def run_etl():
    """
    Run the full ETL process: fetch and load all data types.
    """
    print("Fetching Pokémon...")
    load_to_postgres("pokemon", fetch_pokemon())
    print("Fetching Items...")
    load_to_postgres("items", fetch_items())
    print("Fetching Moves...")
    load_to_postgres("moves", fetch_moves())
    print("Fetching Generations...")
    load_to_postgres("generations", fetch_generations())
    print("✅ ETL process completed.")

if __name__ == "__main__":
    run_etl()

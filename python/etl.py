import requests
import psycopg2
import time
import json


BASE_URL = "https://pokeapi.co/api/v2"
LIMIT = 10000  # change to None for all data


def fetch_data(endpoint, limit=LIMIT):
    url = f"{BASE_URL}/{endpoint}"
    if limit:
        url += f"?limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]


def fetch_detail(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_pokemon(limit=LIMIT):
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
            time.sleep(0.5)
    return data


def fetch_items(limit=LIMIT):
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

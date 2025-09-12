import marimo

__generated_with = "0.15.3"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    return mo, pd


@app.cell
def _():
    import os
    import sqlalchemy

    _password = os.environ.get("POSTGRES_PASSWORD", "password")

    DATABASE_URL = f"postgresql+psycopg2://user:{_password}@postgres:5432/pokemon_db"

    engine = sqlalchemy.create_engine(DATABASE_URL)
    return (engine,)


@app.cell(disabled=True)
def _(mo):
    mo.md(
        r"""
    import psycopg2
    import pandas as pd

    # Connect to Postgres (same credentials as Docker Compose)
    conn = psycopg2.connect(
        dbname="pokemon_db",
        user="user",
        password="password",
        host="postgres",  # if running inside Docker
        port=5432
    )

    # List of tables you want
    tables = ["pokemon", "items", "moves", "generations"]

    # Load each into a DataFrame
    dfs = {}
    for table in tables:
        dfs[table] = pd.read_sql(f"SELECT * FROM {table}", conn)

    # Close connection
    conn.close()

    # Access like this:
    pokemon_df = dfs["pokemon"]
    items_df = dfs["items"]
    moves_df = dfs["moves"]
    generations_df = dfs["generations"]
    """
    )
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE VIEW pokemon_flat AS
        SELECT
            id,
            name,
            -- Flatten JSON stats into columns
            (stats ->> 'hp')::int AS hp,
            (stats ->> 'speed')::int AS speed,
            (stats ->> 'attack')::int AS attack,
            (stats ->> 'defense')::int AS defense,
            (stats ->> 'special-attack')::int AS special_attack,
            (stats ->> 'special-defense')::int AS special_defense,
            height,
            weight,
            base_experience,
            -- Convert arrays into comma-separated strings
            array_to_string(abilities, ', ') AS abilities,
            array_to_string(types, ', ') AS types,
            array_to_string(moves, ', ') AS moves
        FROM
            pokemon
        ORDER BY
            id ASC;
        """,
        engine=engine
    )
    return


@app.cell
def _(engine, pd):
    # Load the view into a DataFrame
    pokemon_flat = pd.read_sql("SELECT * FROM pokemon_flat", engine)
    return (pokemon_flat,)


@app.cell
def _(mo, pd, pokemon_flat):
    # Get unique types
    unique_types = sorted(pd.Series(pokemon_flat['types'].str.split(', ')).explode().unique())

    # Create dropdown UI
    selected_type = mo.ui.dropdown(
        options=["All"] + unique_types,
        label="Select Pokémon Type - > ",
    )

    # Display dropdown
    selected_type
    return (selected_type,)


@app.cell
def _(mo, pd, pokemon_flat):

    # Get unique moves
    unique_moves = sorted(pd.Series(pokemon_flat['moves'].str.split(', ')).explode().unique())

    # Dropdown for moves
    selected_move = mo.ui.dropdown(
        options=["All"] + unique_moves,
        label="Select Pokémon Move - > ",
    )

    selected_move
    return (selected_move,)


@app.cell
def _(engine, pd):
    # Load generation table into pandas (assuming you already have SQLAlchemy engine)
    generation_df = pd.read_sql("SELECT * FROM generations", engine)
    return (generation_df,)


@app.cell
def _(generation_df, mo, pd):
    unique_genarations= sorted(pd.Series(generation_df['name']).unique())
    # Create dropdown for generations
    selected_generation = mo.ui.dropdown(
        options=["All"] + unique_genarations,
        label="Select Generation - > ",
    )

    # Display dropdown
    selected_generation
    return (selected_generation,)


@app.cell
def _(mo, pokemon_flat):
    height_slider = mo.ui.range_slider(
        label="Height range",
        start=float(pokemon_flat['height'].min()),
        stop=float(pokemon_flat['height'].max()),
        step=1,
        value=[float(pokemon_flat['height'].min()), float(pokemon_flat['height'].max())]
    )
    height_slider
    return (height_slider,)


@app.cell
def _(mo, pokemon_flat):
    # Weight slider
    weight_slider = mo.ui.range_slider(
        label="Weight range",
        start=float(pokemon_flat['weight'].min()),
        stop=float(pokemon_flat['weight'].max()),
        step=1,
        value=[float(pokemon_flat['weight'].min()), float(pokemon_flat['weight'].max())]
    )
    weight_slider
    return (weight_slider,)


@app.cell
def _(mo, pokemon_flat):
    # Base Experience slider
    exp_slider = mo.ui.range_slider(
        label="Base Experience range",
        start=float(pokemon_flat['base_experience'].min()),
        stop=float(pokemon_flat['base_experience'].max()),
        step=1,
        value=[float(pokemon_flat['base_experience'].min()), float(pokemon_flat['base_experience'].max())]
    )
    exp_slider
    return (exp_slider,)


@app.cell
def _(mo):
    mo.md(
        rf"""
    # 
    #Pokemon Filtered Table
    ####Click through to filter to customize your table
    """
    )
    return


@app.cell
def _(
    exp_slider,
    generation_df,
    height_slider,
    mo,
    pokemon_flat,
    selected_generation,
    selected_move,
    selected_type,
    weight_slider,
):
    # Start with full DataFrame
    df_filtered = pokemon_flat.copy()

    # --- Filter by Type ---
    t = selected_type.value
    if t != "All":
        df_filtered = df_filtered[df_filtered['types'].str.contains(t)]

    # --- Filter by Move ---
    m = selected_move.value
    if m != "All":
        df_filtered = df_filtered[df_filtered['moves'].str.contains(m)]

    # --- Filter by Height ---
    df_filtered = df_filtered[
        (df_filtered['height'] >= height_slider.value[0]) &
        (df_filtered['height'] <= height_slider.value[1])
    ]

    # --- Filter by Weight ---
    df_filtered = df_filtered[
        (df_filtered['weight'] >= weight_slider.value[0]) &
        (df_filtered['weight'] <= weight_slider.value[1])
    ]

    # --- Filter by Base Experience ---
    df_filtered = df_filtered[
        (df_filtered['base_experience'] >= exp_slider.value[0]) &
        (df_filtered['base_experience'] <= exp_slider.value[1])
    ]

    # --- Filter by Generation ---
    g = selected_generation.value
    if g != "All":
        # Grab the Pokémon list for this generation
        gen_pokemon = generation_df.loc[generation_df['name'] == g, 'pokemon_species'].values[0]

        # Ensure it's parsed into a Python list if stored as text/JSON
        if isinstance(gen_pokemon, str):
            import ast
            gen_pokemon = ast.literal_eval(gen_pokemon)

        # Filter main dataframe
        df_filtered = df_filtered[df_filtered['name'].isin(gen_pokemon)]

    # Display filtered table
    mo.ui.table(
        df_filtered,
        page_size=25

    )
    return


@app.cell
def _(mo):
    mo.md(
        rf"""
    # 
    ##Pokemon Moves Table
    """
    )
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM moves
        """,
        engine=engine
    )
    return


@app.cell
def _(mo):
    mo.md(
        rf"""
    # 
    ##Pokemon Items Table
    """
    )
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM items
        """,
        engine=engine
    )
    return


@app.cell
def _(mo):
    mo.md(
        rf"""
    # 
    ##Pokemon Generation Table
    """
    )
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        SELECT * FROM generations
        """,
        engine=engine
    )
    return


if __name__ == "__main__":
    app.run()

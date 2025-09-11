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

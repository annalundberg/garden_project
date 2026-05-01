"""
Garden Database - SQLite Setup Script
 
Creates garden.db with 3 tables:
  - plant_id   : garden plant catalogue (name + cultivar = unique plant)
  - harvest    : harvest window(s) per unique plant (name + cultivar)
  - lifecycle  : individual planting records

"""

import sqlite3
from pathlib import Path
import pandas as pd


DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"


def create_garden_database():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")   # enforce FK constraints in SQLite
    cursor = conn.cursor()
    cursor.executescript("""
    -- ── Table 1: plant_id ───────────────────────────────────────────────────
    -- Master plant catalogue. (name, cultivar) together identify a unique plant.
    CREATE TABLE IF NOT EXISTS plant_id (
        plant_id      INTEGER       PRIMARY KEY AUTOINCREMENT,
        produce_cat   VARCHAR(10)   NOT NULL,        -- e.g. 'vegetable', 'fruit', 'herb'
        name          VARCHAR(20)   NOT NULL,         -- e.g. 'tomato'
        cultivar      VARCHAR(15)   NOT NULL,         -- e.g. 'Roma', 'Cherokee Purple'
        genus         VARCHAR(15),
        species       VARCHAR(15),
        UNIQUE (name, cultivar)                       -- a cultivar can only appear once per name
    );

    -- ── Table 2: harvest ────────────────────────────────────────────────────
    -- Harvest season window, keyed to plant name.
    CREATE TABLE IF NOT EXISTS harvest (
        harvest_id    INTEGER       PRIMARY KEY AUTOINCREMENT,
        category      CHAR(5)       NOT NULL,         -- e.g. 'early', 'main', 'late'
        start_month   INTEGER       NOT NULL CHECK (start_month BETWEEN 1 AND 12),
        end_month     INTEGER       NOT NULL CHECK (end_month   BETWEEN 1 AND 12),
        name          VARCHAR(20)   NOT NULL,
        cultivar      VARCHAR(15)   NOT NULL,
        UNIQUE (name, cultivar, category),            -- one harvest window per category per plant
        FOREIGN KEY (name, cultivar) REFERENCES plant_id (name, cultivar)
            ON UPDATE CASCADE ON DELETE CASCADE
        
    );

    -- ── Table 3: lifecycle ──────────────────────────────────────────────────
    -- Individual planting records, linked to a specific (name, cultivar) in plant_id.
    CREATE TABLE IF NOT EXISTS lifecycle (
        lifecycle_id  INTEGER       PRIMARY KEY AUTOINCREMENT,
        name          VARCHAR(20)   NOT NULL,
        cultivar      VARCHAR(15)   NOT NULL,
        plant_date    DATE,                           -- ISO format: YYYY-MM-DD
        end_year      INTEGER,                        -- 4-digit year, e.g. 2025
        FOREIGN KEY (name, cultivar) REFERENCES plant_id (name, cultivar)
            ON UPDATE CASCADE ON DELETE CASCADE
    );

    """)

    conn.commit()
    conn.close()
    print(f"Database created at: {DB_PATH}")
    print("Tables: plant_id, harvest, lifecycle")
    return None



if __name__ == "__main__":
    
    create_garden_database()


'''
Data Entry Functions
'''

import sqlite3
from pathlib import Path
import pandas as pd
import math

from db_util import DB_PATH



def nan_to_none(value):
    '''
    Convert a NaN or empty string value to None for safe SQLite insertion.
 
    Parameters:
    value : any, The value to check.
 
    Returns:
    None if the value is NaN or an empty string, otherwise the original value.
    '''
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value

def add_data(produce_cat:str, name:str, cultivar:str, genus:str, species:str, 
             harvest_windows:list[list], p_date:str, p_end:int):
    '''
    Insert a new plant entry across the plant_id, harvest, and lifecycle tables.

    Parameters:
    produce_cat : varchar(10), Produce category for the plant (e.g. 'greens', 'legume').
    name : varchar(20), Common name of the plant (e.g. 'kale', 'snap peas'). SHARED KEY
    cultivar : varchar(15), Cultivar name (e.g. 'Red Russian', 'Sugar Daddy'). 
        part of composite key with name
    genus : varchar(15), Genus of the plant (e.g. 'Brassica').
    species : varchar(15), Species of the plant (e.g. 'oleracea').
    harvest_windows : list[list], One or more harvest windows, each as a 3-element list:
            [category (str), start_month (int), end_month (int)], (e.g. [['early', 5, 7], ['late', 9, 11]])
    p_date : DATE, Planting date in ISO format 'YYYY-MM-DD', or None.
    p_end : YEAR, Year the plant lifecycle ends as a 4-digit integer (e.g. 2025), or None.
    '''
    h_windows = []
    for window in harvest_windows:
        [h_cat, mm_s, mm_e] = window
        h_windows.append((str(h_cat), int(mm_s), int(mm_e), str(name), str(cultivar)))
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
 
    ## Table 1: plant_id
    cursor.execute("""SELECT COUNT(*) FROM plant_id WHERE name = ? AND cultivar = ?""", (name, cultivar))
    if cursor.fetchone()[0] > 0:
        print(f"! Skipped plant_id: '{name}' ({cultivar}) already exists.")
    else:
        cursor.execute("""
            INSERT INTO plant_id (produce_cat, name, cultivar, genus, species)
            VALUES (?, ?, ?, ?, ?)""", (produce_cat, name, cultivar, genus, species))
    ## Table 2: harvest 
    for h_cat, mm_s, mm_e, h_name, h_cultivar in h_windows:
        cursor.execute("""SELECT COUNT(*) FROM harvest WHERE name = ? AND cultivar = ? AND category = ?""", 
                       (h_name, h_cultivar, h_cat))
        if cursor.fetchone()[0] > 0:
            print(f"! Skipped harvest: '{name}' category '{h_cat}' already exists.")
        else:
            cursor.execute("""
                INSERT INTO harvest (category, start_month, end_month, name, cultivar)
                VALUES (?, ?, ?, ?, ?)""", (h_cat, mm_s, mm_e, h_name, h_cultivar))
    ## Table 3: lifecycle 
    cursor.execute("""SELECT COUNT(*) FROM lifecycle WHERE name = ? AND cultivar = ?""", (name, cultivar))
    if cursor.fetchone()[0] > 0:
        print(f"! Skipped lifecycle: '{name}' ({cultivar}) already exists.")
    else:
        cursor.execute("""
            INSERT INTO lifecycle (name, cultivar, plant_date, end_year)
            VALUES (?, ?, ?, ?)""", (name, cultivar, p_date, p_end))
 
    conn.commit()
    conn.close()
 
    print("{} ({}) check and/or insert attempt complete.".format(name,cultivar))
    return None


def add_data_from_df(harvest_df:pd.DataFrame) -> None:
    '''
    Parse dataframe and use add_data fxn to row-wise add new entries to DB

    Parameters:
        df: pretty specific dataframe plant inventory for streamlined data entry
    '''
    for i in harvest_df.index:
        produce,name,cult,genus,species,pdate,pend=harvest_df.loc[i,['produce_cat','plant_name','cultivar','genus','species','plant_date','plant_end']]
        pdate = nan_to_none(pdate)
        pend = None if pd.isna(pend) else int(pend)
        hsa,hea,hsb,heb = harvest_df.loc[i,['harvest_start_a','harvest_end_a','harvest_start_b','harvest_end_b']]
        if hsb > 0:
            h_window = [['early',hsa,hea],['late',hsb,heb]]
        else:
            h_window = [['main',hsa,hea]]
        print(name,cult,sep=', ')
        add_data(produce,name,cult,genus,species,h_window,pdate,pend)
    return None


def parse_harvest_windows(raw_windows: list[str]) -> list[list]:
    '''
    Parse harvest window strings into structured lists. Each window string must follow 
    the format 'category:start_month:end_month', e.g. 'main:4:12' or 'early:5:7'.
 
    Parameters:
    raw_windows : list[str], List of harvest window strings in 'category:start:end' format.
 
    Returns
    list[list], List of [category, start_month, end_month] lists.
 
    Raises
    ValueError, If any window string is not in the expected 'category:start:end' format.
    '''
    windows = []
    for w in raw_windows:
        parts = w.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid harvest window '{w}'. "
                f"Expected format is 'category:start_month:end_month' e.g. 'main:4:12'."
            )
        category, start, end = parts
        windows.append([category.strip(), int(start), int(end)])
    return windows


def prompt_harvest_windows() -> list[list]:
    '''
    Interactively prompt the user to enter one or more harvest windows.
    Continues prompting until the user enters 'done'. Each window is entered
    as 'category:start_month:end_month', e.g. 'main:4:12'.
 
    Returns
    list[list], List of [category, start_month, end_month] lists.
    '''
    windows = []
    print("  Enter harvest windows as 'category:start_month:end_month' (e.g. 'main:4:12').")
    print("  Type 'done' when finished.")
    while True:
        raw = input("  Harvest window: ").strip()
        if raw.lower() == "done":
            if not windows:
                print("! At least one harvest window is required.")
                continue
            break
        try:
            windows.extend(parse_harvest_windows([raw]))
            print(f" Added: {raw}")
        except ValueError as e:
            print(f"! Failure! {e}")
    return windows


def main() -> None:
    '''
    Interactively prompt the user for plant details and call add_data()
    Required fields are re-prompted until a non-empty value is provided. Optional fields accept
    a blank entry to skip (p_date and p_end only).
    '''
    print("Add a new plant to the garden database",'-'*42, sep='\n')
    # required fields
    produce_cat = input("Produce category (e.g. greens):   ").strip()
    name        = input("Plant name (e.g. kale):            ").strip()
    cultivar    = input("Cultivar (e.g. Red Russian):       ").strip()
    genus       = input("Genus (e.g. Brassica):             ").strip()
    species     = input("Species (e.g. napus):              ").strip()

    # harvest windows
    print("Harvest windows:")
    harvest_windows = prompt_harvest_windows()

    # Optional fields
    p_date = input("Planting date YYYY-MM-DD (or leave blank): ").strip() or None
    p_end_raw = input("End year (or leave blank):                 ").strip()
    p_end  = int(p_end_raw) if p_end_raw else None
 
    # Confirm before inserting
    print("\n------ Summary -------")
    print(f"  Name:        {name} ({cultivar})")
    print(f"  Category:    {produce_cat}")
    print(f"  Genus:       {genus} {species}")
    print(f"  Harvest:     {harvest_windows}")
    print(f"  Plant date:  {p_date or '—'}")
    print(f"  End year:    {p_end or '—'}")
    print("-"*42)
 
    confirm = input("Insert into database? [y/n]: ").strip().lower()
    if confirm != "y":
        print("! Cancelled — nothing was inserted.")
        return None
 
    add_data(produce_cat=produce_cat,name=name,cultivar=cultivar,genus=genus,species=species,
             harvest_windows=harvest_windows,p_date=p_date,p_end=p_end)
    return None
 
if __name__ == "__main__":
    main()
    
    # example data add: red russian kale
    # add_data('greens','kale','Red Russian','Brassica','napus',[['main',4,12]],'2026-03-01',2026)

    ## add existing csv inventory to DB
    # harvest_df = pd.read_csv("./garden_edibles_init.csv")
    # add_data_from_df(harvest_df)
'''
Data Entry Functions
'''

import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"

def nan_to_none(value):
    return None if pd.isna(value) else value

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
 
# if __name__ == "__main__":
    
    # example data add: red russian kale
    # add_data('greens','kale','Red Russian','Brassica','napus',[['main',4,12]],'2026-03-01',2026)

    ## add existing csv inventory to DB
    # harvest_df = pd.read_csv("./garden_edibles_init.csv")
    # for i in harvest_df.index:
    #     produce,name,cult,genus,species,pdate,pend=harvest_df.loc[i,['produce_cat','plant_name','cultivar','genus','species','plant_date','plant_end']]
    #     pdate = nan_to_none(pdate)
    #     pend = None if pd.isna(pend) else int(pend)
    #     hsa,hea,hsb,heb = harvest_df.loc[i,['harvest_start_a','harvest_end_a','harvest_start_b','harvest_end_b']]
    #     if hsb > 0:
    #         h_window = [['early',hsa,hea],['late',hsb,heb]]
    #     else:
    #         h_window = [['main',hsa,hea]]
    #     print(name,cult,sep=', ')
    #     add_data(produce,name,cult,genus,species,h_window,pdate,pend)
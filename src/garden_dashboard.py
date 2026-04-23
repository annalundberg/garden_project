'''
Garden Tracking Dashboard with Streamlit + SQLite

Requires:
    garden_dashboard.py: UI and visualizations
    garden.db: SQLite db containg all garden data
'''

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import plotly.express as px


#### DB helper functions ####

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   # lets you access columns by name
    return conn
 
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame."""
    conn = get_connection()
    return pd.read_sql_query(sql, conn, params=params)
 
def execute(sql: str, params: tuple = ()):
    """Run an INSERT / UPDATE / DELETE."""
    conn = get_connection()
    conn.execute(sql, params)
    conn.commit()


#### Config ####
DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"
st.set_page_config(page_title="My Seattle Garden Dashboard", layout="wide")
# @st.cache_resource          # one shared connection for the whole session
 


## quick test harvest visualization ##
# harvest_df = pd.read_csv("garden_edibles_harvest.csv")
# mm_harvest = pd.DataFrame({'Month':pd.Series(dtype=int),
#                            'category':pd.Series(dtype=str),
#                            'variety':pd.Series(dtype=int)})
# for i in range(12):
#     m=i+1
#     print(m)
#     m_harvest = harvest_df.loc[(harvest_df['harvest_start_month']<=m)&(harvest_df['harvest_end_month']>=m)].copy(deep=False)
#     print(m_harvest)
#     cat_count = m_harvest[['category','variety']].groupby('category').count().reset_index()
#     cat_count['Month']=m
#     mm_harvest = pd.concat([mm_harvest,cat_count])
# px.line(mm_harvest, x='Month', y='variety', color='category')
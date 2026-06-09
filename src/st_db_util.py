'''
SQLite garden DB util functions.
Leverages db_util, but includes streamlit specific application.
'''
import sqlite3
import pandas as pd
import streamlit as st

from db_util import DB_PATH, get_connection

@st.cache_resource          # one shared connection for the whole session
def get_cached_connection():
    return get_connection()


def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    '''
    Execute a SELECT statement and return results as a DataFrame.
 
    Parameters:
    sql : A parameterised SQL SELECT statement using ? placeholders.
    params : tuple, optional
        Values to bind to the ? placeholders. Defaults to empty tuple.
 
    Returns:
    Query results with column names matching the SELECT clause.
    '''
    return pd.read_sql_query(sql, get_cached_connection(), params=params)
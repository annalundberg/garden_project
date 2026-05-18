'''
Garden Database Management Page

Access from main dashboard:
streamlit run src/1_garden_dashboard.py
'''

import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

from db_util import execute
from st_db_util import query


DB_PATH = Path(__file__).parent.parent.parent / "data" / "garden.db"
MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        font-weight: 300;
    }
    .stApp {
        background-color: #f5f0e8;
    }
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #2c3e2d;
        margin-bottom: 0;
    }
    .page-subtitle {
        font-family: 'Lato', sans-serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #7a8c6e;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.3rem;
        font-weight: 400;
        font-style: italic;
        color: #2c3e2d;
        border-bottom: 1px solid #c4a668;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
    }
    .result-card {
        background: #ffffff;
        border: 1px solid #ddd5c0;
        border-left: 4px solid #6b8f5e;
        border-radius: 6px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .result-card .plant-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: #2c3e2d;
    }
    .result-card .cultivar-name {
        font-size: 0.85rem;
        color: #7a8c6e;
        font-style: italic;
    }
    .not-found {
        color: #a08060;
        font-style: italic;
        font-size: 0.9rem;
        padding: 0.5rem 0;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 2.5rem; }
</style>
"""


def render_plant_lookup() -> None:
    '''
    Render the plant lookup section.
    Accepts a plant name as input and returns all matching cultivars
    from plant_id, along with produce category and taxonomy.
    '''
    st.markdown('<div class="section-header">Look up a plant</div>', unsafe_allow_html=True)
    name_input = st.text_input("Plant name", placeholder="e.g. kale", key="lookup_name")
    if not st.button("Search", key="btn_lookup"):
        return
    name_clean = name_input.strip().lower()
    if not name_clean:
        st.warning("Please enter a plant name to search.")
        return
    df = query("""
        SELECT name, cultivar, produce_cat, genus, species
        FROM   plant_id
        WHERE  LOWER(name) = ?
        ORDER  BY cultivar""",(name_clean,))
    if df.empty:
        st.markdown(f'<div class="not-found">No entries found for "{name_clean}" in the database.</div>',
                    unsafe_allow_html=True)
        return
    st.success(f"Found {len(df)} cultivar(s) for **{name_clean}**:")
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class="result-card">
            <div class="plant-name">{row['name'].title()}</div>
            <div class="cultivar-name">{row['cultivar']}</div>
            <div style="font-size:0.8rem; color:#7a8c6e; margin-top:0.3rem;">
                {row['produce_cat']} &nbsp;·&nbsp;
                <em>{row['genus']} {row['species']}</em>
            </div>
        </div>""", unsafe_allow_html=True)
    return


def main() -> None:
    '''
    Configure and render the database management page.
    '''
    st.set_page_config(page_title="Garden Database", page_icon="🗃️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="page-title">🗃️ Database Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">inspect and edit your garden records</div>', unsafe_allow_html=True)

    render_plant_lookup()
    return None


if __name__ == "__main__":
    main()

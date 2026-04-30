'''
Garden Tracking Dashboard with Streamlit + SQLite

Requires:
    garden_dashboard.py: UI and visualizations
    garden.db: SQLite db containg all garden data
'''

import sqlite3
import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"
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
        background-image:
            radial-gradient(circle at 20% 20%, rgba(139,170,110,0.12) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(196,166,104,0.10) 0%, transparent 50%);
    }
    .garden-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #2c3e2d;
        letter-spacing: -0.5px;
        line-height: 1.1;
        margin-bottom: 0;
    }
    .garden-subtitle {
        font-family: 'Lato', sans-serif;
        font-weight: 300;
        font-size: 1rem;
        color: #7a8c6e;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 400;
        font-style: italic;
        color: #2c3e2d;
        border-bottom: 1px solid #c4a668;
        padding-bottom: 0.4rem;
        margin-bottom: 1.2rem;
    }
    .harvest-card {
        background: linear-gradient(135deg, #ffffff 60%, #f0ebe0);
        border: 1px solid #ddd5c0;
        border-left: 4px solid #6b8f5e;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 2px 3px 12px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .harvest-card:hover {
        transform: translateY(-2px);
        box-shadow: 2px 6px 18px rgba(0,0,0,0.09);
    }
    .harvest-card .plant-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #2c3e2d;
    }
    .harvest-card .cultivar-name {
        font-size: 0.85rem;
        color: #7a8c6e;
        font-style: italic;
        margin-top: 0.1rem;
    }
    .harvest-card .meta-row {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .harvest-card .tag {
        font-size: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #eef4e8;
        color: #4a6741;
        border: 1px solid #b8d4a8;
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
    }
    .harvest-card .tag.category {
        background: #fdf6e3;
        color: #8a6a1f;
        border-color: #e2c97e;
    }
    .empty-state {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #9aaa8e;
        font-style: italic;
        font-size: 1rem;
    }
    .month-badge {
        display: inline-block;
        background: #2c3e2d;
        color: #f5f0e8;
        font-family: 'Lato', sans-serif;
        font-size: 0.8rem;
        font-weight: 400;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.3rem 0.9rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
    }
    .category-label {
        font-family: 'Lato', sans-serif;
        font-size: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #7a8c6e;
        margin: 1.2rem 0 0.6rem 0;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 2.5rem; }
</style>
"""

#### DB helper functions ####
@st.cache_resource          # one shared connection for the whole session
def get_connection() -> sqlite3.Connection:
    '''
    Create and cache a single SQLite connection for the Streamlit session.
 
    Returns:
    sqlite3.Connection- A shared connection with foreign key enforcement enabled and
    row_factory set to sqlite3.Row for column-name access.
    '''
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
 
 
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
    return pd.read_sql_query(sql, get_connection(), params=params)

### UI helper functions ###
def build_harvest_card(name: str, cultivar: str, category: str, start_month: int, end_month: int) -> str:
    '''
    Build an HTML string for a single harvest card.
 
    Parameters:
    name : Common plant name, displayed in title case.
    cultivar : Cultivar name, displayed in italics.
    produce_cat : Produce category tag (e.g. 'greens', 'legume').
    category : Harvest category tag (e.g. 'main', 'early', 'late').
    start_month : Harvest window start month as an integer (1-12).
    end_month : Harvest window end month as an integer (1-12).
 
    Returns:
    An HTML string rendering the harvest card.
    '''
    window = f"{MONTH_NAMES[start_month]} – {MONTH_NAMES[end_month]}"
    h_card = f"""<div class="harvest-card">
        <div class="plant-name">{name.title()}</div>
        <div class="cultivar-name">{cultivar}</div>
        <div class="meta-row">
            <span class="tag category">{category}</span>
            <span class="tag">🗓 {window}</span>
        </div>
    </div>"""
    return h_card


def render_harvest_section(current_month: int, month_name: str, year: int) -> None:
    '''
    Query and render the 'Ready to harvest' section for the current month.
    Displays a 3-column grid of harvest cards for all plants whose harvest window includes the 
    current month. Shows an empty-state message if no plants are in season.
 
    Parameters:
    current_month : The current month as an integer (1-12).
    month_name : The current month as a full string (e.g. 'April').
    year : The current year as a 4-digit integer (e.g. 2026).
    '''
    st.markdown('<div class="section-header">Ready to harvest</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="month-badge">🗓 {month_name} {year}</div>',unsafe_allow_html=True)
    df = query("""
        SELECT
            p.name, p.cultivar, p.produce_cat, h.category, h.start_month, h.end_month
        FROM   harvest h
        JOIN   plant_id p
            ON h.name = p.name AND h.cultivar = p.cultivar
        WHERE  h.start_month <= ? AND h.end_month >= ?
        ORDER  BY p.produce_cat, p.name, p.cultivar
        """, (current_month, current_month))
    if df.empty:
        st.markdown(f'<div class="empty-state">🌱 Nothing to harvest in {month_name} — check back soon.</div>',
                    unsafe_allow_html=True)
        return None
    for produce_cat, group in df.groupby("produce_cat"):
        st.markdown(f'<div class="category-label">{produce_cat.title()}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(group.iterrows()):
            card = build_harvest_card(name=row["name"],cultivar=row["cultivar"],category=row["category"],
                                      start_month=row["start_month"],end_month=row["end_month"])
            with cols[i % 3]:
                st.markdown(card, unsafe_allow_html=True)
    return None

### main dash function ###
def main() -> None:
    '''
    Configure and render the My Seattle Garden Streamlit dashboard. Sets the page config, injects custom CSS, 
    renders the page header, and calls each dashboard section in order.
    '''
    st.set_page_config(page_title="My Seattle Garden", page_icon="🌿", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    # Header
    st.markdown('<div class="garden-title">🌿 My Seattle Garden</div>', unsafe_allow_html=True)
    st.markdown('<div class="garden-subtitle">Pacific Northwest growing journal</div>',unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # sections
    today = datetime.date.today()
    render_harvest_section(current_month=today.month, month_name=today.strftime("%B"), year=today.year)
    return None

if __name__ == "__main__":
    main()
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
        background-color: #2d4a2d;
    }
    .page-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #f5f0e8;
        margin-bottom: 0;
    }
    .page-subtitle {
        font-family: 'Lato', sans-serif;
        font-weight: 300;
        font-size: 0.95rem;
        color: #a8c4a8;
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
        color: #f5f0e8;
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
        color: #c8b898;
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


def render_harvest_browser() -> None:
    '''
    Render the harvest table browser section. Provides a cascading 
    produce category → plant name dropdown that filters and 
    displays matching harvest window entries.
    '''
    st.markdown('<div class="section-header">Browse harvest windows</div>', unsafe_allow_html=True)
    # Produce category dropdown
    categories = query(
        "SELECT DISTINCT produce_cat FROM plant_id ORDER BY produce_cat"
        )["produce_cat"].tolist()
    selected_cat = st.selectbox("Produce category", options=["— select —"] + categories,
                                key="harvest_cat",)
    if selected_cat == "— select —":
        return
    # Plant name dropdown — auto-populated from selected category
    names = query("SELECT DISTINCT name FROM plant_id WHERE produce_cat = ? ORDER BY name",
                  (selected_cat,),)["name"].tolist()
    selected_name = st.selectbox("Plant name", options=["— select —"] + names, key="harvest_name",)
    if selected_name == "— select —":
        return
    # Harvest windows for selected plant
    df = query("""
        SELECT h.harvest_id, h.cultivar, h.category, h.start_month, h.end_month
        FROM   harvest h
        WHERE  LOWER(h.name) = ?
        ORDER  BY h.cultivar, h.start_month
        """, (selected_name.lower(),),)
    if df.empty:
        st.markdown(f'<div class="not-found">No harvest windows found for "{selected_name}".</div>',
                    unsafe_allow_html=True)
        return
    st.dataframe(df.assign(start_month=df["start_month"].map(MONTH_NAMES),
                           end_month=df["end_month"].map(MONTH_NAMES),
                           ).rename(columns={"harvest_id": "ID", "cultivar": "Cultivar", 
                                             "category": "Category", "start_month": "Start", 
                                             "end_month": "End",}),
                            use_container_width=True, hide_index=True,)
    return None


def render_harvest_editor() -> None:
    '''
    Render the harvest window add/edit interface.

    Allows the user to select an existing (name, cultivar) pair from
    plant_id and either add a new harvest window or edit an existing one.
    All changes are written directly to the harvest table.
    '''
    st.markdown('<div class="section-header">Add or edit a harvest window</div>', unsafe_allow_html=True)

    ## Plant selection ##
    col1, col2 = st.columns(2)
    with col1:
        all_names = query("SELECT DISTINCT name FROM plant_id ORDER BY name")["name"].tolist()
        edit_name = st.selectbox("Plant name", ["— select —"] + all_names, key="edit_name")
    if edit_name == "— select —":
        return
    with col2:
        cultivars = query("SELECT DISTINCT cultivar FROM plant_id WHERE name = ? ORDER BY cultivar",
                          (edit_name,))["cultivar"].tolist()
        edit_cultivar = st.selectbox("Cultivar", ["— select —"] + cultivars, key="edit_cultivar")
    if edit_cultivar == "— select —":
        return
    ## Existing windows ##
    existing = query("""
        SELECT harvest_id, category, start_month, end_month
        FROM   harvest
        WHERE  name = ? AND cultivar = ?
        ORDER  BY start_month
        """, (edit_name, edit_cultivar),)
    ## Add new window ##
    with st.expander("➕ Add a new harvest window", expanded=not existing.empty is False):
        new_cat   = st.text_input("Category (e.g. main, early, late)", key="new_cat").strip()
        col3, col4 = st.columns(2)
        with col3:
            new_start = st.selectbox("Start month", list(MONTH_NAMES.values()), key="new_start")
        with col4:
            new_end   = st.selectbox("End month",   list(MONTH_NAMES.values()), key="new_end")
        if st.button("Add harvest window", key="btn_add"):
            start_int = [k for k, v in MONTH_NAMES.items() if v == new_start][0]
            end_int   = [k for k, v in MONTH_NAMES.items() if v == new_end][0]
            if not new_cat:
                st.error("Category is required.")
            else:
                try:
                    execute("""
                        INSERT INTO harvest (category, start_month, end_month, name, cultivar)
                        VALUES (?, ?, ?, ?, ?)
                        """, (new_cat, start_int, end_int, edit_name, edit_cultivar),)
                    st.success(f"✅ Added '{new_cat}' window ({new_start}–{new_end}) for {edit_name} ({edit_cultivar}).")
                    st.cache_resource.clear()
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"⚠️ A '{new_cat}' harvest window already exists for {edit_name} ({edit_cultivar}).")
    ## Edit existing windows ##
    if existing.empty:
        return
    st.markdown("**Existing harvest windows** — select one to edit:")
    window_options = {
        f"{row['category']}  ({MONTH_NAMES[row['start_month']]}–{MONTH_NAMES[row['end_month']]})  [ID {row['harvest_id']}]": row
        for _, row in existing.iterrows()
    }
    selected_window = st.selectbox("Harvest window", options=["— select —"] + list(window_options.keys()),
                                   key="edit_window",)
    if selected_window == "— select —":
        return
    row = window_options[selected_window]
    col5, col6, col7 = st.columns(3)
    with col5:
        upd_cat   = st.text_input("Category", value=row["category"], key="upd_cat").strip()
    with col6:
        month_list = list(MONTH_NAMES.values())
        upd_start = st.selectbox("Start month", month_list, index=row["start_month"] - 1,key="upd_start",)
    with col7:
        upd_end   = st.selectbox("End month", month_list, index=row["end_month"] - 1, key="upd_end",)
    col8, col9 = st.columns([1, 1])
    with col8:
        if st.button("💾 Save changes", key="btn_save"):
            start_int = [k for k, v in MONTH_NAMES.items() if v == upd_start][0]
            end_int   = [k for k, v in MONTH_NAMES.items() if v == upd_end][0]
            execute("""
                UPDATE harvest
                SET    category = ?, start_month = ?, end_month = ?
                WHERE  harvest_id = ?
                """,(upd_cat, start_int, end_int, int(row["harvest_id"])),)
            st.success("✅ Harvest window updated.")
            st.cache_resource.clear()
            st.rerun()
    with col9:
        if st.button("🗑️ Delete window", key="btn_delete"):
            execute("DELETE FROM harvest WHERE harvest_id = ?",(int(row["harvest_id"]),))
            st.success("✅ Harvest window deleted.")
            st.cache_resource.clear()
            st.rerun()
    return None


def main() -> None:
    '''
    Configure and render the database management page.
    '''
    st.set_page_config(page_title="Garden Database", page_icon="🗃️", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown('<div class="page-title">🗃️ Database Manager</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">inspect and edit your garden records</div>', unsafe_allow_html=True)

    render_plant_lookup()
    render_harvest_browser()
    render_harvest_editor()
    return None


if __name__ == "__main__":
    main()

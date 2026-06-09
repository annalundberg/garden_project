'''
Garden Tracking Dashboard with Streamlit + SQLite

Data sources:
    garden.db: SQLite db containg all garden data
    open meteo: open source weather data via requests
'''

# import sqlite3
import datetime
from pathlib import Path
import pandas as pd
import streamlit as st
import requests

from st_db_util import query
from weather_graphics import get_weather_graphic

DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"
LAT, LON = 47.4502, -122.3088               ## SEATAC coordinates for weather data
PRECIP_WARNING_CM = 2.5                     ## minimum weekly precip recommendation
MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 
               7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

## Dashboard Page Design ##
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
        color: #2c3e2d;
        margin: 1.2rem 0 0.6rem 0;
    }
    .coming-soon-card {
        background: linear-gradient(135deg, #f8f5ee 60%, #ede8db);
        border: 1px solid #ddd5c0;
        border-left: 4px solid #c4a668;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 2px 3px 12px rgba(0,0,0,0.03);
        opacity: 0.85;
    }
    .coming-soon-card .plant-name {
        font-family: 'Playfair Display', serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #6b6050;
    }
    .coming-soon-card .cultivar-name {
        font-size: 0.85rem;
        color: #a89880;
        font-style: italic;
        margin-top: 0.1rem;
    }
    .coming-soon-card .meta-row {
        display: flex;
        gap: 1rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .coming-soon-card .tag {
        font-size: 0.75rem;
        font-weight: 400;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: #fdf6e3;
        color: #8a6a1f;
        border: 1px solid #e2c97e;
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
    }
    .weather-strip {
        background: linear-gradient(135deg, #2c3e2d 0%, #3d5c3a 100%);
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        gap: 0rem;
    }
    .weather-stat {
        flex: 1;
        min-width: 120px;
        text-align: center;
        padding: 0.4rem 0.8rem;
        border-right: 1px solid rgba(255,255,255,0.12);
    }
    .weather-stat:last-child { border-right: none; }
    .weather-stat .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: #f5f0e8;
        line-height: 1.1;
    }
    .weather-stat .stat-label {
        font-size: 0.7rem;
        font-weight: 400;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #9ab88a;
        margin-top: 0.2rem;
    }
    .weather-stat .stat-sub {
        font-size: 0.78rem;
        color: #b8c9a8;
        margin-top: 0.15rem;
    }
    .precip-warning {
        background: rgba(74,130,195,0.15);
        border: 1px solid #4a82c3;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        color: #4a82c3;
        font-size: 0.85rem;
        margin-top: 0.6rem;
        letter-spacing: 0.03em;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding-top: 2.5rem; }
</style>
"""


## weather helpers ##
@st.cache_data(ttl=1800)
def fetch_weather() -> dict:
    '''
    Fetch current conditions and the past 7 days of weather for SeaTac
    from the Open-Meteo API. Results are cached for 30 minutes.

    Returns
        Parsed JSON response containing:
        - current: temperature_2m, precipitation, relative_humidity_2m,
                   wind_speed_10m
        - daily:   temperature_2m_max, temperature_2m_min,
                   precipitation_sum (past 7 days including today)
    Raises
        requests.HTTPError, if the Open-Meteo API returns a non-2xx response.
    '''
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": LAT, "longitude": LON, "hourly": "soil_temperature_6cm",
              "current": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m,weather_code",
              "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
              "temperature_unit": "celsius", "wind_speed_unit": "kmh", "precipitation_unit": "mm",
              "timezone": "US/Pacific", "past_days": 7, "forecast_days": 1}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def render_weather_section() -> None:
    '''
    Fetch and render the weather strip at the top of the dashboard. 
    Displays four stats in a dark green strip:
        Current temperature (°C/F), Current humidity (%), 
        Current wind speed (mph), Current precipitation (cm)
    Below the strip, shows a 7-day summary row:
        Overnight low / daytime high range averaged over the past 7 days
        Total precipitation over the past 7 days (today inclusive)
    A warning is displayed if total 7-day precipitation is below PRECIP_WARNING_CM.
    '''
    try:
        data = fetch_weather()
    except Exception as e:
        st.warning(f"⚠️ Weather data unavailable: {e}")
        with st.expander("🔍 Debug — API request params"):
            st.json({"latitude": LAT, "longitude": LON, "hourly": "soil_temperature_6cm",
                "current": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "celsius", "wind_speed_unit": "kmh", "precipitation_unit": "mm",
                "timezone": "US/Pacific", "past_days": 7, "forecast_days": 1})
        return
    current, daily, hourly = data["current"], data["daily"], data["hourly"]
    temp_c = current["temperature_2m"]
    temp_f = round(temp_c * 9 / 5 + 32, 1)
    humidity = current["relative_humidity_2m"]
    wind_kmh = current["wind_speed_10m"]
    wind_mph = round(wind_kmh * 0.621371, 1)
    precip_now = current["precipitation"]/10 # mm to cm
    graphic = get_weather_graphic(current['weather_code'])
    avg_low_c = round(sum(daily["temperature_2m_min"]) / len(daily["temperature_2m_min"]), 1)
    avg_high_c = round(sum(daily["temperature_2m_max"]) / len(daily["temperature_2m_max"]), 1)
    avg_low_f = round(avg_low_c * 9 / 5 + 32, 1)
    avg_high_f = round(avg_high_c * 9 / 5 + 32, 1)
    total_precip = round(sum(daily["precipitation_sum"])/10, 2) # mm to cm
    # Average soil temp — filter out None values from hourly data
    soil_temps = [v for v in hourly["soil_temperature_6cm"] if v is not None]
    avg_soil_c = round(sum(soil_temps) / len(soil_temps), 1) if soil_temps else None
    avg_soil_f = round(avg_soil_c * 9 / 5 + 32, 1) if avg_soil_c is not None else None
    soil_display = f"{avg_soil_c:.0f}°C" if avg_soil_c is not None else "—"
    soil_sub = f"{avg_soil_f:.0f}°F" if avg_soil_f is not None else ""
    ## current conditions strip ##
    current_html = f"""
        <div class="weather-stat">
            <div class="stat-value">{temp_c:.0f}°C</div>
            <div class="stat-label">Temperature</div>
            <div class="stat-sub">{temp_f:.0f}°F</div>
        </div>
        <div class="weather-stat">
            <div class="stat-value">{humidity}%</div>
            <div class="stat-label">Humidity</div>
        </div>
        <div class="weather-stat">
            <div class="stat-value">{wind_kmh:.0f} km/h</div>
            <div class="stat-label">Wind Speed</div>
            <div class="stat-sub">{wind_mph:.0f} mph</div>
        </div>
        <div class="weather-stat">
            <div class="stat-value">{precip_now:.2f} cm</div>
            <div class="stat-label">Precipitation</div>
        </div>
    </div>"""
    graphic_html = (
        '<div class="weather-stat" style="flex:0 0 90px; border-right: 1px solid rgba(255,255,255,0.12);">'
        + graphic["svg"]
        + '<div class="stat-label" style="margin-top:0.3rem;">' + graphic["label"] + "</div>"
        + "</div>"
    )
    st.markdown('<div class="weather-strip">' + graphic_html + current_html + "</div>",unsafe_allow_html=True)
    
    ## 7-day summary strip ##
    st.markdown(f"""
    <div class="weather-strip">
        <div class="weather-stat">
            <div class="stat-value">{avg_low_c:.0f}° – {avg_high_c:.0f}°C</div>
            <div class="stat-label">7-Day Avg Temp Range</div>
            <div class="stat-sub">{avg_low_f:.0f}° – {avg_high_f:.0f}°F &nbsp;|&nbsp; avg low / high</div>
        </div>
        <div class="weather-stat">
            <div class="stat-value">{soil_display}</div>
            <div class="stat-label">7-Day Avg Soil Temp</div>
            <div class="stat-sub">{soil_sub} &nbsp;|&nbsp; 6cm depth, hourly metric</div>
        </div>
        <div class="weather-stat">
            <div class="stat-value">{total_precip:.2f} cm</div>
            <div class="stat-label">7-Day Precipitation</div>
            <div class="stat-sub">past 7 days including today</div>
        </div>
    </div>""", unsafe_allow_html=True)
    ## supplemental water warning ##
    if total_precip < PRECIP_WARNING_CM:
        st.markdown(f'<div class="precip-warning">'
            f'💧 Only {total_precip:.2f} cm of rain in the past 7 days — '
            f'supplemental watering is recommended.'
            f'</div>', unsafe_allow_html=True)
    return None


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


def render_harvest_section(current_month:int, month_name:str, year:int) -> None:
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
        SELECT  p.name, p.cultivar, p.produce_cat, h.category, h.start_month, h.end_month
        FROM  harvest h
        JOIN  plant_id p
               ON h.name = p.name AND h.cultivar = p.cultivar
        JOIN  lifecycle l
               ON l.name = p.name AND l.cultivar = p.cultivar
        WHERE  h.start_month <= ? AND h.end_month >= ? AND (l.end_year IS NULL OR l.end_year >= ?)
        ORDER  BY p.produce_cat, p.name, p.cultivar""", (current_month, current_month, year))
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


def build_coming_soon_card(name: str, cultivar: str, category: str,
                           start_month: int, end_month: int) -> str:
    '''
    Build an HTML string for a single coming soon card.
 
    Styled with muted amber tones to visually distinguish upcoming
    harvests from currently available ones.
 
    Parameters
    name : Common plant name, displayed in title case.
    cultivar : Cultivar name, displayed in italics.
    category : Harvest category tag (e.g. 'main', 'early', 'late').
    start_month : Harvest window start month as an integer (1-12).
    end_month : Harvest window end month as an integer (1-12).
 
    Returns
        An HTML string rendering the coming soon card.
    '''
    window = f"{MONTH_NAMES[start_month]} – {MONTH_NAMES[end_month]}"
    soon_card = f"""<div class="coming-soon-card">
        <div class="plant-name">{name.title()}</div>
        <div class="cultivar-name">{cultivar}</div>
        <div class="meta-row">
            <span class="tag">{category}</span>
            <span class="tag">🗓 {window}</span>
        </div>
    </div>"""
    return soon_card
 
 
def render_coming_soon_section(next_month:int, next_month_name:str, year:int) -> None:
    '''
    Query and render the 'Coming soon' section for next month's produce.
    Excludes plants already harvestable this month to show only those newly coming into season. 
    Plants are grouped by produce category. Shows an empty-state message if nothing is coming into season.
 
    Parameters:
    current_month : The current month as an integer (1-12).
    month_name : The current month as a full string (e.g. 'April').
    year : The current year as a 4-digit integer (e.g. 2026).
    '''
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Coming soon</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="month-badge">🗓 {next_month_name} {year}</div>', unsafe_allow_html=True)
 
    df = query("""
               SELECT  p.name, p.cultivar, p.produce_cat, h.category, h.start_month, h.end_month
               FROM  harvest h
               JOIN  plant_id p
                    ON  h.name = p.name AND h.cultivar = p.cultivar
               JOIN  lifecycle l
                    ON l.name = p.name AND l.cultivar = p.cultivar
               WHERE  h.start_month <= ? AND h.end_month >= ? AND  h.start_month > ?
                AND (l.end_year IS NULL OR l.end_year >= ?)
               ORDER  BY p.produce_cat, p.name, p.cultivar""", (next_month, next_month, next_month - 1, year))
 
    if df.empty:
        st.markdown(f'<div class="empty-state">🌱 Nothing new coming into season in {next_month_name}.</div>',
                    unsafe_allow_html=True)
        return None
 
    for produce_cat, group in df.groupby("produce_cat"):
        st.markdown(f'<div class="category-label">{produce_cat.title()}</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(group.iterrows()):
            card = build_coming_soon_card(name=row["name"], cultivar=row["cultivar"], category=row["category"],
                                          start_month=row["start_month"], end_month=row["end_month"])
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
    st.markdown('<div class="garden-title">🌿 My Seattle Home Garden</div>', unsafe_allow_html=True)
    st.markdown('<div class="garden-subtitle">Fruits, Vegetable and Herbs</div>',unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # sections
    today = datetime.date.today()
    next_month = today.month % 12 + 1
    next_year  = today.year + 1 if today.month == 12 else today.year
    render_weather_section()
    render_harvest_section(current_month=today.month, month_name=today.strftime("%B"), year=today.year)
    render_coming_soon_section(next_month=next_month, next_month_name=datetime.date(today.year, next_month, 1).strftime("%B"),
                               year=next_year if today.month == 12 else today.year)
    return None

if __name__ == "__main__":
    main()
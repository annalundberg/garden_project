# Garden Project
Garden edibles tracking and projection project. Just for fun.

## Remember to activate the environment

'''
source garden_env/bin/activate
'''

## Launching the Dashboard

'''
streamlit run src/1_garden_dashboard.py
'''

## Helpful functions for updating & checking database

- SQLite Database creation function lives in src/garden_db_creator.py
    - create_garden_db() is a good reference for database structure & expectations

- Dashboard independent database addition functions live in src/garden_db_add.py
    - use add_data module to add new entries, follow prompts given

```
python -m add_data
```

- check existing produce_cat before adding a new entry

```python
import sqlite3
from db_util import DB_PATH

with sqlite3.connect(DB_PATH) as conn:
    categories = conn.execute('SELECT DISTINCT produce_cat FROM plant_id ORDER BY produce_cat').fetchall()
print([row[0] for row in categories])
```

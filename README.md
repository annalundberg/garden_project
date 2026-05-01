# Garden Project
Garden edibles tracking and projection project. Just for fun.


## Helpful functions for updating & checking database

- SQLite Database creation function lives in src/garden_db_creator.py
    - create_garden_db() is a good reference for database structure & expectations

- Database updating functions live in src/garden_db_add.py
    - example of adding a fully new entry, with Russian Red Kale

```python
add_data('greens','kale','Red Russian','Brassica','napus',[['main',4,12]],'2026-03-01',2026)
```

- check existing produce_cat before adding a new entry

```python
import sqlite3
from garden_db_creator import DB_PATH
with sqlite3.connect(DB_PATH) as conn:
    categories = conn.execute('SELECT DISTINCT produce_cat FROM plant_id ORDER BY produce_cat').fetchall()
print([row[0] for row in categories])
```

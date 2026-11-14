"""Load cleaned CSV entities into a local SQLite database using sql/schema.sql."""
import csv, sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
db=ROOT/'data'/'cleaned'/'pharmacy_analytics.sqlite'
if db.exists(): db.unlink()
conn=sqlite3.connect(db)
conn.execute('PRAGMA foreign_keys=ON')
conn.executescript((ROOT/'sql'/'schema.sql').read_text(encoding='utf-8'))
for table in ['pharmacies','products','orders','order_items','inventory','delivery_events']:
    with (ROOT/'data'/'cleaned'/f'{table}.csv').open(newline='',encoding='utf-8') as f:
        rows=csv.DictReader(f); cols=rows.fieldnames
        sql=f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
        conn.executemany(sql, ([r[c] for c in cols] for r in rows))
conn.commit()
print(f'Created {db}')
print('Loaded row counts:')
for t in ['pharmacies','products','orders','order_items','inventory','delivery_events']:
    print(f'{t}: {conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]}')
conn.close()

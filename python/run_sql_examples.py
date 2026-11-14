"""Execute every statement in sql/business_analysis.sql against the local SQLite DB."""
import sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
db=ROOT/'data'/'cleaned'/'pharmacy_analytics.sqlite'
sql=(ROOT/'sql'/'business_analysis.sql').read_text(encoding='utf-8')
conn=sqlite3.connect(db)
pending=''; index=0
for line in sql.splitlines():
    if line.lstrip().startswith('--'): continue
    pending+=line+'\n'
    if sqlite3.complete_statement(pending):
        statement=pending.strip(); pending=''
        if not statement: continue
        index+=1
        try:
            cur=conn.execute(statement)
            print(f'Query {index}: {cur.rowcount if cur.rowcount >= 0 else cur.description and "result rows"}')
            for row in cur.fetchmany(5): print('  ',row)
        except sqlite3.Error as exc:
            print(f'Query {index} failed: {exc}')
            raise
if pending.strip(): raise RuntimeError('Trailing incomplete SQL statement')
conn.close()

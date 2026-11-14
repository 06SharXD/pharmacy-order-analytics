"""Validate referential integrity and business rules in cleaned CSVs (stdlib only)."""
import csv, sys
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'cleaned'
def load(name):
    with (DATA/f'{name}.csv').open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
orders=load('orders'); items=load('order_items'); products=load('products'); pharmacies=load('pharmacies'); inv=load('inventory'); events=load('delivery_events')
with (ROOT/'data_quality'/'issue_register.csv').open(newline='',encoding='utf-8') as f: issue_rows=list(csv.DictReader(f))
checks=[]
def check(name, ok, detail): checks.append((name,bool(ok),detail))
oids=[r['order_id'] for r in orders]; pids={r['product_id'] for r in products}; phids={r['pharmacy_id'] for r in pharmacies}
check('unique order IDs',len(oids)==len(set(oids)),f'{len(oids)} rows')
try:
    for r in orders: datetime.strptime(r['order_ts'],'%Y-%m-%d %H:%M:%S')
    valid_order_times=True
except ValueError:
    valid_order_times=False
check('parseable order timestamps',valid_order_times,'all cleaned order_ts values parse as YYYY-MM-DD HH:MM:SS')
check('order pharmacy keys',all(r['pharmacy_id'] in phids for r in orders),'all order pharmacy keys resolve')
check('item order keys',all(r['order_id'] in set(oids) for r in items),'all item order keys resolve')
check('item product keys',all(r['product_id'] in pids for r in items),'all item product keys resolve')
check('positive quantities',all(int(r['quantity'])>0 for r in items),'all quantities > 0')
check('inventory keys',all(r['pharmacy_id'] in phids and r['product_id'] in pids for r in inv),'all inventory keys resolve')
check('delivered event timestamp',all(e['delivered_ts'] for e in events if next(o for o in orders if o['order_id']==e['order_id'])['order_status']=='delivered'),'all delivered orders have a delivery timestamp')
order_map={r['order_id']:r for r in orders}
event_map={r['order_id']:r for r in events}
documented_missing={r['record_key'] for r in issue_rows if r['issue_code']=='DELIVERED_WITHOUT_DELIVERY_TS'}
missing_delivered={o['order_id'] for o in orders if o['order_status']=='delivered' and (o['order_id'] not in event_map or not event_map[o['order_id']]['delivered_ts'])}
check('missing delivered times documented',missing_delivered <= documented_missing,f'{len(missing_delivered)} delivered order(s) excluded from elapsed-time KPI and listed in issue register')
try:
    monotonic=all(datetime.strptime(event_map[o['order_id']]['delivered_ts'],'%Y-%m-%d %H:%M:%S') >= datetime.strptime(o['order_ts'],'%Y-%m-%d %H:%M:%S') for o in orders if o['order_status']=='delivered' and o['order_id'] in event_map and event_map[o['order_id']]['delivered_ts'])
except (ValueError,KeyError):
    monotonic=False
check('nonnegative delivered duration',monotonic,'delivered timestamp is present and not earlier than order timestamp')
for name,ok,detail in checks: print(f"{'PASS' if ok else 'FAIL'} | {name} | {detail}")
sys.exit(0 if all(x[1] for x in checks) else 1)

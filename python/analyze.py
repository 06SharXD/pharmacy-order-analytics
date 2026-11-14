"""Recompute key synthetic KPIs from cleaned CSVs using Python's standard library."""
import csv,json,statistics
from collections import Counter,defaultdict
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'/'cleaned'
def load(n):
    with (DATA/f'{n}.csv').open(newline='',encoding='utf-8') as f: return list(csv.DictReader(f))
orders=load('orders'); items=load('order_items'); events={r['order_id']:r for r in load('delivery_events')}; inventory=load('inventory')
value=defaultdict(float)
for it in items: value[it['order_id']]+=float(it['line_amount'])
mins=[]; within=0; delivered=0; cancel=0; cities=defaultdict(lambda:[0,0]); customers=Counter()
for o in orders:
    customers[o['customer_id']]+=1; cities[o['city']][0]+=1
    cancel += o['order_status']=='cancelled'; cities[o['city']][1]+=o['order_status']=='cancelled'
    if o['order_status']=='delivered' and o['order_id'] in events:
        e=events[o['order_id']]; m=(datetime.strptime(e['delivered_ts'],'%Y-%m-%d %H:%M:%S')-datetime.strptime(o['order_ts'],'%Y-%m-%d %H:%M:%S')).total_seconds()/60
        mins.append(m); delivered+=1; within+=m<=360
metrics={'synthetic_data':True,'clean_orders':len(orders),'clean_order_items':len(items),'delivered_orders_with_valid_duration':delivered,'delivered_within_6h_rate':round(within/delivered,4),'average_fulfillment_hours':round(statistics.mean(mins)/60,2),'cancellation_rate':round(cancel/len(orders),4),'delivered_order_value_total':round(sum(value[o['order_id']] for o in orders if o['order_status']=='delivered'),2),'repeat_customer_rate':round(sum(n>1 for n in customers.values())/len(customers),4),'inventory_at_or_below_reorder_point_rows':sum(int(x['on_hand_qty'])<=int(x['reorder_point']) for x in inventory),'city_cancellation_rates':{c:round(v[1]/v[0],4) for c,v in cities.items()}}
(ROOT/'reports'/'metrics_recomputed.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))

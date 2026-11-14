from __future__ import annotations
import csv, json, random, sqlite3, statistics
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == 'python' else HERE.parent / 'outputs' / 'pharmacy-order-analytics'
RAW = ROOT / 'data' / 'raw'
CLEAN = ROOT / 'data' / 'cleaned'
for d in [RAW, CLEAN, ROOT/'excel', ROOT/'sql', ROOT/'powerbi', ROOT/'requirements', ROOT/'documentation', ROOT/'data_quality', ROOT/'reports', ROOT/'resume', ROOT/'python']:
    d.mkdir(parents=True, exist_ok=True)
random.seed(20261114)

def write_csv(path, rows):
    rows=list(rows)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
def read_csv(path):
    with path.open(newline='', encoding='utf-8') as f: return list(csv.DictReader(f))

cities=['Bengaluru','Chennai','Hyderabad','Pune','Mumbai','Delhi']
pharmacies=[]
for i in range(1,13):
    city=cities[(i-1)//2]
    pharmacies.append({'pharmacy_id':f'PH{i:03}','pharmacy_name':f'{city} Pharmacy {1+(i-1)%2}','city':city,'region':{'Bengaluru':'South','Chennai':'South','Hyderabad':'South','Pune':'West','Mumbai':'West','Delhi':'North'}[city],'capacity_band':['Small','Medium','Large'][(i-1)%3]})
products=[]
cats=['Prescription','OTC','Wellness','Personal Care','Devices']
for i in range(1,46):
    cat=cats[(i-1)%5]
    products.append({'product_id':f'PR{i:03}','product_name':f'{cat} Product {i:02}','category':cat,'unit_price':round(random.uniform(45,1500),2),'prescription_required':str(cat=='Prescription').lower()})
write_csv(RAW/'pharmacies.csv', pharmacies); write_csv(RAW/'products.csv',products)

orders=[]; items=[]; events=[]
start=datetime(2025,1,1)
statuses=['delivered']*78+['cancelled']*12+['returned']*3+['processing']*7
for i in range(1,1001):
    oid=f'OR{i:05}'; created=start+timedelta(minutes=random.randrange(365*24*60))
    ph=random.choice(pharmacies); status=random.choice(statuses)
    customer=f'C{random.randint(1,380):04}'
    orders.append({'order_id':oid,'customer_id':customer,'pharmacy_id':ph['pharmacy_id'],'order_ts':created.strftime('%Y-%m-%d %H:%M:%S'),'order_status':status,'channel':random.choice(['App','Web','Call Center']),'city':ph['city']})
    for _ in range(random.randint(1,4)):
        p=random.choice(products); qty=random.randint(1,4)
        items.append({'order_item_id':f'IT{len(items)+1:06}','order_id':oid,'product_id':p['product_id'],'quantity':qty,'unit_price':p['unit_price'],'line_amount':round(qty*p['unit_price'],2)})
    if status in ('delivered','returned'):
        valid=created+timedelta(minutes=random.randint(10,90))
        dispatch=valid+timedelta(minutes=random.randint(15,120))
        delivery=dispatch+timedelta(minutes=random.randint(30,480))
        events.append({'order_id':oid,'prescription_validated_ts':valid.strftime('%Y-%m-%d %H:%M:%S'),'packed_ts':(valid+timedelta(minutes=random.randint(8,50))).strftime('%Y-%m-%d %H:%M:%S'),'dispatched_ts':dispatch.strftime('%Y-%m-%d %H:%M:%S'),'delivered_ts':delivery.strftime('%Y-%m-%d %H:%M:%S'),'event_source':'synthetic_simulation'})
    else: events.append({'order_id':oid,'prescription_validated_ts':'','packed_ts':'','dispatched_ts':'','delivered_ts':'','event_source':'synthetic_simulation'})
write_csv(RAW/'orders.csv',orders); write_csv(RAW/'order_items.csv',items); write_csv(RAW/'delivery_events.csv',events)

inventory=[]
for ph in pharmacies:
  for p in products:
    inventory.append({'inventory_id':f'IV{len(inventory)+1:06}','pharmacy_id':ph['pharmacy_id'],'product_id':p['product_id'],'on_hand_qty':random.randint(0,75),'reorder_point':random.randint(5,18),'expiry_date':(start+timedelta(days=random.randint(50,850))).date().isoformat(),'snapshot_date':'2025-12-31'})
write_csv(RAW/'inventory.csv',inventory)
# Plant controlled anomalies in the raw orders/items/events: visible and logged, excluded from cleaned model.
orders[11]['pharmacy_id']=''; orders[24]['order_ts']='not-a-date'; orders[31]['order_status']='DELIVERED '
orders[44]['order_id']=orders[43]['order_id']
items[8]['quantity']='-2'; items[15]['product_id']='PR999'
delivered_event=next(e for e in events if next(o for o in orders if o['order_id']==e['order_id'])['order_status']=='delivered')
delivered_event['delivered_ts']=''
write_csv(RAW/'orders.csv',orders); write_csv(RAW/'order_items.csv',items); write_csv(RAW/'delivery_events.csv',events)

# Cleaning: duplicate order id keeps first record; malformed timestamp, missing pharmacy, invalid status excluded/quarantined.
phids={x['pharmacy_id'] for x in pharmacies}; prodids={x['product_id'] for x in products}; orderids={x['order_id'] for x in orders}
issues=[]; seen=set(); clean_orders=[]
for n,o in enumerate(orders,2):
    if o['order_id'] in seen:
        issues.append({'source_table':'orders','source_row':n,'record_key':o['order_id'],'issue_code':'DUPLICATE_ORDER_ID','severity':'High','disposition':'Quarantined duplicate; first occurrence retained','business_impact':'Could double count orders and revenue'}); continue
    seen.add(o['order_id'])
    try: datetime.strptime(o['order_ts'],'%Y-%m-%d %H:%M:%S')
    except ValueError:
        issues.append({'source_table':'orders','source_row':n,'record_key':o['order_id'],'issue_code':'INVALID_ORDER_TIMESTAMP','severity':'High','disposition':'Quarantined; timestamp not parseable','business_impact':'Cannot assign to reporting period or calculate elapsed time'}); continue
    if o['pharmacy_id'] not in phids:
        issues.append({'source_table':'orders','source_row':n,'record_key':o['order_id'],'issue_code':'MISSING_OR_UNKNOWN_PHARMACY','severity':'High','disposition':'Quarantined from pharmacy-level analysis','business_impact':'Cannot attribute performance to pharmacy'}); continue
    status=o['order_status'].strip().lower()
    if status not in {'delivered','cancelled','returned','processing'}:
        issues.append({'source_table':'orders','source_row':n,'record_key':o['order_id'],'issue_code':'NONCANONICAL_STATUS','severity':'Medium','disposition':f"Normalized '{o['order_status']}' to '{status}'",'business_impact':'Status splits or misstates rates'}); o['order_status']=status
    else: o['order_status']=status
    clean_orders.append(o)
valid_oid={o['order_id'] for o in clean_orders}
clean_items=[]
for n,it in enumerate(items,2):
    if int(it['quantity'])<=0:
        issues.append({'source_table':'order_items','source_row':n,'record_key':it['order_item_id'],'issue_code':'NONPOSITIVE_QUANTITY','severity':'High','disposition':'Quarantined invalid line','business_impact':'Would reduce or distort item and revenue totals'}); continue
    if it['product_id'] not in prodids:
        issues.append({'source_table':'order_items','source_row':n,'record_key':it['order_item_id'],'issue_code':'UNKNOWN_PRODUCT','severity':'High','disposition':'Quarantined unresolved product key','business_impact':'Cannot classify item or join product attributes'}); continue
    if it['order_id'] in valid_oid: clean_items.append(it)
clean_events=[]
for n,e in enumerate(events,2):
    o=next((x for x in clean_orders if x['order_id']==e['order_id']),None)
    if not o: continue
    if o['order_status']=='delivered' and not e['delivered_ts']:
        issues.append({'source_table':'delivery_events','source_row':n,'record_key':e['order_id'],'issue_code':'DELIVERED_WITHOUT_DELIVERY_TS','severity':'High','disposition':'Quarantined from elapsed-time KPI','business_impact':'Fulfilment duration is unavailable'}); continue
    clean_events.append(e)
for name, rows in [('orders',clean_orders),('order_items',clean_items),('products',products),('inventory',inventory),('pharmacies',pharmacies),('delivery_events',clean_events)]:
    write_csv(CLEAN/f'{name}.csv',rows)
write_csv(ROOT/'data_quality'/'issue_register.csv',issues)

# Reproducible metrics from cleaned data.
evmap={e['order_id']:e for e in clean_events}; item_by=defaultdict(list)
for it in clean_items: item_by[it['order_id']].append(it)
phmap={p['pharmacy_id']:p for p in pharmacies}; rows=[]
for o in clean_orders:
    e=evmap.get(o['order_id']); mins=None
    if e and o['order_status']=='delivered': mins=(datetime.strptime(e['delivered_ts'],'%Y-%m-%d %H:%M:%S')-datetime.strptime(o['order_ts'],'%Y-%m-%d %H:%M:%S')).total_seconds()/60
    rows.append({'order_id':o['order_id'],'customer_id':o['customer_id'],'pharmacy_id':o['pharmacy_id'],'city':o['city'],'order_ts':o['order_ts'],'order_status':o['order_status'],'channel':o['channel'],'net_order_value':round(sum(float(x['line_amount']) for x in item_by[o['order_id']]),2),'fulfillment_minutes':mins})
delivered=[r for r in rows if r['order_status']=='delivered' and r['fulfillment_minutes'] is not None]
completed=len(delivered); total=len(rows); within6=sum(x['fulfillment_minutes']<=360 for x in delivered)
revenue=sum(r['net_order_value'] for r in rows if r['order_status']=='delivered')
city_ct=Counter(); city_cancel=Counter()
for r in rows: city_ct[r['city']]+=1; city_cancel[r['city']]+=r['order_status']=='cancelled'
phmins=defaultdict(list)
for r in delivered: phmins[r['pharmacy_id']].append(r['fulfillment_minutes'])
invlow=[x for x in inventory if int(x['on_hand_qty'])<=int(x['reorder_point'])]
metrics={'synthetic_data':True,'seed':20261114,'raw_orders_including_duplicate_row':len(orders),'clean_orders':len(rows),'clean_order_items':len(clean_items),'delivered_orders_with_valid_duration':completed,'delivered_within_6h_rate':round(within6/completed,4) if completed else None,'average_fulfillment_hours':round(statistics.mean(x['fulfillment_minutes'] for x in delivered)/60,2),'delivered_order_value_total':round(revenue,2),'cancellation_rate':round(sum(r['order_status']=='cancelled' for r in rows)/total,4),'repeat_customer_rate':round(sum(1 for c,n in Counter(r['customer_id'] for r in rows).items() if n>1)/len(set(r['customer_id'] for r in rows)),4),'inventory_at_or_below_reorder_point_rows':len(invlow),'intentional_data_quality_issues':len(issues),'city_cancellation_rates':{c:round(city_cancel[c]/city_ct[c],4) for c in city_ct},'pharmacy_avg_fulfillment_minutes':{ph:round(statistics.mean(vals),1) for ph,vals in phmins.items()}}
(ROOT/'reports'/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
write_csv(ROOT/'powerbi'/'fact_orders.csv',rows)
write_csv(ROOT/'excel'/'order_detail_import.csv',rows)

# Excel workbook, using formula-based summary/report and pivot-ready source tables.
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter
wb=Workbook(); ws=wb.active; ws.title='KPI Summary'
ws.append(['Synthetic Pharmacy Operations Analytics','Value','Definition'])
formulas=[('Clean orders',"=COUNTA(tblOrders[order_id])",'Order rows after documented cleaning'),('Delivered orders',"=COUNTIF(tblOrders[order_status],\"delivered\")",'Orders in delivered status'),('Cancellation rate',"=COUNTIF(tblOrders[order_status],\"cancelled\")/COUNTA(tblOrders[order_id])",'Cancelled / clean orders'),('Delivered value',"=SUMIFS(tblOrders[net_order_value],tblOrders[order_status],\"delivered\")",'Synthetic line value for delivered orders'),('Average fulfillment hours',"=AVERAGEIFS(tblOrders[fulfillment_minutes],tblOrders[order_status],\"delivered\")/60",'Order timestamp to delivery timestamp'),('Within 6 hours',"=COUNTIFS(tblOrders[order_status],\"delivered\",tblOrders[fulfillment_minutes],\">0\",tblOrders[fulfillment_minutes],\"<=360\")/COUNTIFS(tblOrders[order_status],\"delivered\",tblOrders[fulfillment_minutes],\">0\")",'Eligible delivered orders <= 360 elapsed minutes')]
for row in formulas: ws.append(row)
ws['A10']='All values are based on synthetic data. Refresh formulas after replacing/expanding the Excel Table.'
od=wb.create_sheet('Order Detail'); od.append(list(rows[0].keys()))
for r in rows: od.append([r[k] for k in rows[0].keys()])
for sh,name in [(od,'tblOrders')]:
    ref=f'A1:{get_column_letter(sh.max_column)}{sh.max_row}'; tab=Table(displayName=name,ref=ref); tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True,showColumnStripes=False); sh.add_table(tab); sh.freeze_panes='A2'
pa=wb.create_sheet('Pivot Ready'); pa.append(['Suggested pivot: Rows=city, pharmacy_id or order_status; Columns=month(order_ts); Values=Count of order_id / Sum of net_order_value / Average of fulfillment_minutes.']); pa.append(list(rows[0].keys()))
for r in rows: pa.append([r[k] for k in rows[0].keys()])
tab=Table(displayName='tblPivotReady',ref=f'A2:{get_column_letter(len(rows[0]))}{len(rows)+2}'); tab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium4',showRowStripes=True,showColumnStripes=False); pa.add_table(tab)
guide=wb.create_sheet('Refresh Guide',0)
guide_rows=[
 ['Workflow','Instructions'],
 ['Provenance','All records are synthetic. Raw tabs contain planted defects. Cleaned Order Detail is the reporting table; do not calculate KPIs from raw rows.'],
 ['Power Query-ready CSVs','The six source CSVs are in data/raw with stable headers. In Excel use Data > Get Data > From Text/CSV. For a folder-based append, select the data/raw folder and combine only same-entity files with matching headers.'],
 ['Cleaning steps','Trim/lowercase order_status; parse order_ts as Date/Time; quarantine duplicate order_id, invalid timestamp and missing/unknown pharmacy key; quarantine nonpositive item quantity and unknown product key; quarantine delivered orders lacking delivered_ts. Preserve raw values and log each exception.'],
 ['Refresh reporting','Refresh/replace the cleaned output table from data/cleaned/orders.csv after the documented cleaning rules. Extend tblOrders and tblPivotReady to the last row, then recalculate. KPI Summary uses table formulas.'],
 ['Pivot-ready reporting','Create a native PivotTable from tblPivotReady. Example: Rows=city, Columns=order_status, Values=Count of order_id; or Rows=pharmacy_id, Values=Average of fulfillment_minutes and Count of order_id. Add month from order_ts in Power Query or Excel.'],
 ['Refresh limitation','No Power Query connection or native PivotTable cache is embedded. The workbook provides the import/cleaning recipe, source tabs and structured table layouts for a user to configure in Excel.']
]
for r in guide_rows: guide.append(r)
raw_sets=[('Raw Orders',orders,'tblRawOrders'),('Raw Order Items',items,'tblRawOrderItems'),('Raw Products',products,'tblRawProducts'),('Raw Inventory',inventory,'tblRawInventory'),('Raw Pharmacies',pharmacies,'tblRawPharmacies'),('Raw Delivery Events',events,'tblRawDeliveryEvents')]
for title,data,tname in raw_sets:
    sh=wb.create_sheet(title); sh.append(list(data[0].keys()))
    for r in data: sh.append([r[k] for k in data[0].keys()])
    table=Table(displayName=tname,ref=f'A1:{get_column_letter(len(data[0]))}{len(data)+1}'); table.tableStyleInfo=TableStyleInfo(name='TableStyleMedium2',showRowStripes=True,showColumnStripes=False); sh.add_table(table)
qsh=wb.create_sheet('DQ Issue Register'); qsh.append(list(issues[0].keys()))
for r in issues: qsh.append([r[k] for k in issues[0].keys()])
qtab=Table(displayName='tblDQIssues',ref=f'A1:{get_column_letter(len(issues[0]))}{len(issues)+1}'); qtab.tableStyleInfo=TableStyleInfo(name='TableStyleMedium5',showRowStripes=True,showColumnStripes=False); qsh.add_table(qtab)
wb.calculation.fullCalcOnLoad=True; wb.calculation.forceFullCalc=True; wb.calculation.calcMode='auto'
for sh in wb.worksheets:
  sh.freeze_panes='A2'
  for c in sh[1]: c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='174A6E')
  for col in sh.columns:
    letter=get_column_letter(col[0].column); width=min(42,max(12,max(len(str(x.value or '')) for x in list(col)[:300])+2)); sh.column_dimensions[letter].width=width
  for row in sh.iter_rows(min_row=2):
    for c in row:
      if c.data_type=='f': c.number_format='General'
ws['B4'].number_format='0.0%'; ws['B5'].number_format='₹#,##0.00'; ws['B6'].number_format='0.00 "hours"'; ws['B7'].number_format='0.0%'
wb.save(ROOT/'excel'/'pharmacy_operations.xlsx')

# Produce a compact insights report with verified values.
topcity=max(metrics['city_cancellation_rates'],key=metrics['city_cancellation_rates'].get)
topph=max(metrics['pharmacy_avg_fulfillment_minutes'],key=metrics['pharmacy_avg_fulfillment_minutes'].get)
ins=f'''# Business insights (synthetic simulation)\n\nAll figures below were generated from the cleaned CSV model using seed `{metrics['seed']}`. They describe only this constructed scenario and are not PharmEasy or industry results. Re-run `python python/analyze.py` after generation to refresh `reports/metrics.json`.\n\n- **Volume and quality:** {metrics['clean_orders']:,} clean orders were retained from {metrics['raw_orders_including_duplicate_row']:,} raw order rows (one planted duplicate plus quarantined records); {metrics['intentional_data_quality_issues']} planted/observed issue rows are recorded in the issue register.\n- **Fulfilment:** {metrics['delivered_within_6h_rate']:.1%} of {completed:,} eligible delivered orders reached delivery within six hours of order creation. Mean elapsed time was {metrics['average_fulfillment_hours']:.2f} hours. The slowest pharmacy by sample mean was {topph} at {metrics['pharmacy_avg_fulfillment_minutes'][topph]:.1f} minutes; small sample counts should be shown alongside comparisons.\n- **Cancellations:** the clean-order cancellation rate was {metrics['cancellation_rate']:.1%}. {topcity} had the highest city-level synthetic rate at {metrics['city_cancellation_rates'][topcity]:.1%}; this is a prioritization signal for investigation, not a causal finding.\n- **Inventory:** {metrics['inventory_at_or_below_reorder_point_rows']:,} pharmacy-product snapshots were at or below their reorder point. Use these as a replenishment queue candidate, subject to current stock and lead-time validation.\n- **Commercial value:** delivered line-item value totals ₹{metrics['delivered_order_value_total']:,.2f} in the synthetic sample. This is not recognized revenue or a company financial metric.\n\n## Suggested actions for the simulated business\n\n1. Review the highest-delay pharmacy and city cohorts with sample-size context; segment by channel and order hour before assigning causes.\n2. Route inventory rows at/below reorder point to a simulated replenishment review, checking expiry and supplier lead time before action.\n3. Resolve high-severity key/timestamp issues upstream and monitor issue counts by batch before refreshing dashboards.\n4. Keep cancellations, processing orders and missing event times visible; do not silently interpret them as zero-duration fulfilments.\n\n## Limits\n\nThe seed creates a deterministic demonstration dataset. It has no real customer or pharmacy records, no prescription contents or personal health information, no live integrations, no production automation, and no stakeholder validation. The values are suitable for demonstrating SQL, data cleaning, spreadsheet design and BI modeling only.\n'''
(ROOT/'reports'/'business_insights.md').write_text(ins,encoding='utf-8')
print(json.dumps({'root':str(ROOT),'metrics':metrics},indent=2))

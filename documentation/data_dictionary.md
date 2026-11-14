# Data dictionary

All files in this repository are synthetic. Timestamps use local-naive text (`YYYY-MM-DD HH:MM:SS`) solely for this exercise; no timezone conversion is modeled. Money-like fields are synthetic INR-denominated unit values.

| Entity | Primary key | Important fields | Relationships |
|---|---|---|---|
| orders | order_id | customer_id, pharmacy_id, order_ts, order_status, channel, city | pharmacy_id → pharmacies; order_id → order_items and delivery_events |
| order_items | order_item_id | order_id, product_id, quantity, unit_price, line_amount | order_id → orders; product_id → products |
| products | product_id | product_name, category, unit_price, prescription_required | product_id → order_items and inventory |
| inventory | inventory_id | pharmacy_id, product_id, on_hand_qty, reorder_point, expiry_date, snapshot_date | pharmacy_id → pharmacies; product_id → products |
| pharmacies | pharmacy_id | pharmacy_name, city, region, capacity_band | pharmacy_id → orders and inventory |
| delivery_events | order_id | prescription_validated_ts, packed_ts, dispatched_ts, delivered_ts | order_id → orders; one event row per order in generated set |

`data/raw/` contains planted anomalies. `data/cleaned/` contains rows that pass documented cleaning rules. `powerbi/fact_orders.csv` is a denormalized order-level view; use it instead of joining order totals to item-level facts for order metrics.

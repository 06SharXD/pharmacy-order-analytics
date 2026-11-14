-- Synthetic Pharmacy Order Fulfilment & Inventory Analytics model (SQLite-compatible)
PRAGMA foreign_keys = ON;
CREATE TABLE pharmacies (
  pharmacy_id TEXT PRIMARY KEY, pharmacy_name TEXT NOT NULL, city TEXT NOT NULL,
  region TEXT NOT NULL, capacity_band TEXT NOT NULL
);
CREATE TABLE products (
  product_id TEXT PRIMARY KEY, product_name TEXT NOT NULL, category TEXT NOT NULL,
  unit_price REAL NOT NULL CHECK (unit_price >= 0), prescription_required TEXT NOT NULL
);
CREATE TABLE orders (
  order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL,
  pharmacy_id TEXT NOT NULL REFERENCES pharmacies(pharmacy_id), order_ts TEXT NOT NULL,
  order_status TEXT NOT NULL CHECK (order_status IN ('delivered','cancelled','returned','processing')),
  channel TEXT NOT NULL, city TEXT NOT NULL
);
CREATE TABLE order_items (
  order_item_id TEXT PRIMARY KEY, order_id TEXT NOT NULL REFERENCES orders(order_id),
  product_id TEXT NOT NULL REFERENCES products(product_id), quantity INTEGER NOT NULL CHECK(quantity > 0),
  unit_price REAL NOT NULL CHECK(unit_price >= 0), line_amount REAL NOT NULL
);
CREATE TABLE inventory (
  inventory_id TEXT PRIMARY KEY, pharmacy_id TEXT NOT NULL REFERENCES pharmacies(pharmacy_id),
  product_id TEXT NOT NULL REFERENCES products(product_id), on_hand_qty INTEGER NOT NULL,
  reorder_point INTEGER NOT NULL, expiry_date TEXT NOT NULL, snapshot_date TEXT NOT NULL
);
CREATE TABLE delivery_events (
  order_id TEXT PRIMARY KEY REFERENCES orders(order_id), prescription_validated_ts TEXT,
  packed_ts TEXT, dispatched_ts TEXT, delivered_ts TEXT, event_source TEXT NOT NULL
);
CREATE INDEX ix_orders_ts ON orders(order_ts);
CREATE INDEX ix_orders_pharmacy_status ON orders(pharmacy_id, order_status);
CREATE INDEX ix_items_order ON order_items(order_id);
CREATE INDEX ix_inventory_product_pharmacy ON inventory(product_id, pharmacy_id);

-- 1. Join order lines to orders/products, then summarize value and quantity.
SELECT p.category, COUNT(DISTINCT o.order_id) AS orders,
       SUM(oi.quantity) AS units, ROUND(SUM(oi.line_amount), 2) AS item_value
FROM orders o INNER JOIN order_items oi ON oi.order_id=o.order_id
INNER JOIN products p ON p.product_id=oi.product_id
WHERE o.order_status='delivered'
GROUP BY p.category ORDER BY item_value DESC;

-- 2. CTE and date/time elapsed calculations: within six hours from order to delivery.
WITH delivered AS (
  SELECT o.order_id, o.pharmacy_id, o.city,
         (julianday(e.delivered_ts)-julianday(o.order_ts))*24*60 AS fulfillment_minutes
  FROM orders o INNER JOIN delivery_events e ON e.order_id=o.order_id
  WHERE o.order_status='delivered' AND e.delivered_ts IS NOT NULL
), pharmacy_kpis AS (
  SELECT pharmacy_id, COUNT(*) AS delivered_orders,
         AVG(fulfillment_minutes) AS avg_minutes,
         SUM(CASE WHEN fulfillment_minutes <= 360 THEN 1 ELSE 0 END) AS within_6h
  FROM delivered GROUP BY pharmacy_id
)
SELECT p.pharmacy_name, pk.delivered_orders, ROUND(pk.avg_minutes,1) AS avg_minutes,
       ROUND(1.0*pk.within_6h/pk.delivered_orders,4) AS within_6h_rate
FROM pharmacy_kpis pk JOIN pharmacies p USING(pharmacy_id)
ORDER BY avg_minutes DESC;

-- 3. Subquery: cities whose cancellation rate exceeds the overall rate.
SELECT city, 1.0*SUM(CASE WHEN order_status='cancelled' THEN 1 ELSE 0 END)/COUNT(*) AS cancel_rate
FROM orders GROUP BY city
HAVING cancel_rate > (SELECT 1.0*SUM(CASE WHEN order_status='cancelled' THEN 1 ELSE 0 END)/COUNT(*) FROM orders)
ORDER BY cancel_rate DESC;

-- 4. Window functions: rank pharmacies and compare their monthly order volumes.
WITH monthly AS (
  SELECT pharmacy_id, strftime('%Y-%m',order_ts) AS month, COUNT(*) AS orders
  FROM orders GROUP BY pharmacy_id, strftime('%Y-%m',order_ts)
), trend AS (
  SELECT *, LAG(orders) OVER(PARTITION BY pharmacy_id ORDER BY month) AS prior_month_orders,
         RANK() OVER(PARTITION BY month ORDER BY orders DESC) AS monthly_rank
  FROM monthly
)
SELECT *, orders-prior_month_orders AS month_over_month_change FROM trend ORDER BY month, monthly_rank;

-- 5. Inventory conditional aggregation and expiry window.
SELECT p.category, COUNT(*) AS pharmacy_product_rows,
       SUM(CASE WHEN i.on_hand_qty=0 THEN 1 ELSE 0 END) AS zero_stock_rows,
       SUM(CASE WHEN i.on_hand_qty<=i.reorder_point THEN 1 ELSE 0 END) AS at_or_below_reorder,
       SUM(CASE WHEN date(i.expiry_date)<=date(i.snapshot_date,'+90 day') THEN 1 ELSE 0 END) AS expires_in_90d
FROM inventory i JOIN products p USING(product_id) GROUP BY p.category ORDER BY at_or_below_reorder DESC;

-- 6. Repeat customers using a subquery and a LEFT JOIN to retain all customers.
SELECT COUNT(*) AS repeat_customers FROM (
  SELECT customer_id FROM orders GROUP BY customer_id HAVING COUNT(*)>1
);

-- 7. Data-quality checks: duplicate and unresolved keys should return zero rows.
SELECT order_id, COUNT(*) AS n FROM orders GROUP BY order_id HAVING COUNT(*)>1;
SELECT o.order_id FROM orders o LEFT JOIN pharmacies p USING(pharmacy_id) WHERE p.pharmacy_id IS NULL;
SELECT oi.order_item_id FROM order_items oi LEFT JOIN products p USING(product_id) WHERE p.product_id IS NULL;
-- 8. Expected documented exception: this should match DELIVERED_WITHOUT_DELIVERY_TS in issue_register.csv.
SELECT o.order_id FROM orders o LEFT JOIN delivery_events e USING(order_id)
WHERE o.order_status='delivered' AND (e.order_id IS NULL OR e.delivered_ts IS NULL);

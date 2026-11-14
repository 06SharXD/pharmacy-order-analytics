# Power BI setup (no `.pbix` included)

This repository does not contain a Power BI Desktop project file. Load the CSV model below in Power BI Desktop using **Get Data → Text/CSV**. The CSVs are a complete import-ready model; use `data/cleaned` for all dimension and event tables and `powerbi/fact_orders.csv` for the denormalized order-level view. Use one model path only to avoid double-counting.

Recommended approach: use `fact_orders.csv` for order-level KPI pages and relate `fact_orders[pharmacy_id]` to `pharmacies[pharmacy_id]` (many-to-one). Use the normalized cleaned `orders` → `order_items` → `products` tables for product-category analysis, and `inventory` for stock. Keep order-level measures on `fact_orders` or item-level measures on `order_items`; do not sum order values after joining to multiple order lines. Mark a calendar table as the date table and relate it to the order date.

## Measures

```DAX
Orders = COUNTROWS(fact_orders)
Delivered Orders = CALCULATE([Orders], fact_orders[order_status] = "delivered")
Cancelled Orders = CALCULATE([Orders], fact_orders[order_status] = "cancelled")
Cancellation Rate = DIVIDE([Cancelled Orders], [Orders])
Delivered Item Value = CALCULATE(SUM(fact_orders[net_order_value]), fact_orders[order_status] = "delivered")
Average Fulfillment Hours =
    AVERAGEX(FILTER(fact_orders, fact_orders[order_status] = "delivered" && NOT ISBLANK(fact_orders[fulfillment_minutes])),
      fact_orders[fulfillment_minutes] / 60.0)
Within 6 Hours =
    DIVIDE(CALCULATE([Orders], fact_orders[order_status] = "delivered", fact_orders[fulfillment_minutes] <= 360,
      fact_orders[fulfillment_minutes] > 0), [Delivered Orders])
At or Below Reorder =
    COUNTROWS(FILTER(inventory, inventory[on_hand_qty] <= inventory[reorder_point]))
Repeat Customers =
    COUNTROWS(FILTER(VALUES(orders[customer_id]), CALCULATE(COUNTROWS(orders)) > 1))
```

The supplied `fact_orders.csv` already has `fulfillment_minutes` for eligible delivered orders and blanks otherwise. If rebuilding this view from normalized tables, create the elapsed-minute field in Power Query by subtracting order time from delivery time after converting both to Date/Time. Use blank for missing timestamps, never zero.

## Layout specification

1. **Overview:** KPI cards for Orders, Delivered Orders, Cancellation Rate, Average Fulfillment Hours and Delivered Item Value; monthly orders line chart; status/channel stacked bar.
2. **Fulfilment:** pharmacy and city matrix with delivered count, mean hours and within-six-hour rate; histogram by duration; date and channel slicers.
3. **Inventory:** at/below reorder count card; table by pharmacy/product with on-hand, reorder point, expiry date; category bar chart.
4. **Data quality:** issue counts by code/severity and affected rows using `data_quality/issue_register.csv`; do not mix quarantined issue counts into cleaned order KPIs.

All results are synthetic scenario outputs. No Power BI visual or `.pbix` file is represented as already created.

# KPI dictionary

| KPI | Definition | Numerator / denominator | Grain / exclusions |
|---|---|---|---|
| Clean orders | Count of unique retained order IDs | Count of cleaned orders | One order; duplicates and invalid timestamp/pharmacy records excluded |
| Delivered orders | Orders with canonical `delivered` status | Count of delivered orders | One order |
| Cancellation rate | Cancelled orders ÷ clean orders | cancelled / all clean | Processing and returned remain in denominator |
| Fulfilment time | Delivery timestamp minus order timestamp | elapsed minutes / 60 for displayed hours | Delivered orders with both valid timestamps only |
| Within-six-hour rate | Eligible delivered orders with elapsed minutes ≤360 ÷ eligible delivered orders | <=360 / eligible delivered | Delivered orders with valid event times only |
| Delivered item value | Sum of line amounts for delivered orders | sum `line_amount` | Synthetic item value, not accounting revenue |
| Repeat customer rate | Distinct customers with >1 clean order ÷ distinct customers | repeat / observed customers | Not a retention cohort metric |
| At/below reorder | Inventory rows where on-hand quantity ≤ reorder point | count of pharmacy-product snapshots | One snapshot row; not a stockout rate |

All metrics refer to deterministic synthetic data, not PharmEasy or an industry benchmark.

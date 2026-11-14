# Business insights (synthetic simulation)

All figures below were generated from the cleaned CSV model using seed `20261114`. They describe only this constructed scenario and are not PharmEasy or industry results. Re-run `python python/analyze.py` after generation to refresh `reports/metrics.json`.

- **Volume and quality:** 997 clean orders were retained from 1,000 raw order rows (one planted duplicate plus quarantined records); 6 planted/observed issue rows are recorded in the issue register.
- **Fulfilment:** 46.3% of 773 eligible delivered orders reached delivery within six hours of order creation. Mean elapsed time was 6.23 hours. The slowest pharmacy by sample mean was PH012 at 397.1 minutes; small sample counts should be shown alongside comparisons.
- **Cancellations:** the clean-order cancellation rate was 12.9%. Mumbai had the highest city-level synthetic rate at 15.0%; this is a prioritization signal for investigation, not a causal finding.
- **Inventory:** 79 pharmacy-product snapshots were at or below their reorder point. Use these as a replenishment queue candidate, subject to current stock and lead-time validation.
- **Commercial value:** delivered line-item value totals ₹4,066,891.65 in the synthetic sample. This is not recognized revenue or a company financial metric.

## Suggested actions for the simulated business

1. Review the highest-delay pharmacy and city cohorts with sample-size context; segment by channel and order hour before assigning causes.
2. Route inventory rows at/below reorder point to a simulated replenishment review, checking expiry and supplier lead time before action.
3. Resolve high-severity key/timestamp issues upstream and monitor issue counts by batch before refreshing dashboards.
4. Keep cancellations, processing orders and missing event times visible; do not silently interpret them as zero-duration fulfilments.

## Limits

The seed creates a deterministic demonstration dataset. It has no real customer or pharmacy records, no prescription contents or personal health information, no live integrations, no production automation, and no stakeholder validation. The values are suitable for demonstrating SQL, data cleaning, spreadsheet design and BI modeling only.

# Business requirements brief

**Scenario status:** synthetic portfolio exercise; no real PharmEasy data, stakeholder interviews, or production workflow were used.

## Problem statement
A hypothetical pharmacy delivery operation wants a repeatable view of order fulfilment, cancellations and inventory levels. Analysts need to identify where further investigation may help and communicate data-quality exceptions before relying on the report.

## Objectives
- Measure order volume, cancellation share, elapsed fulfilment time and delivered item value.
- Compare pharmacy, city, channel and product category patterns with sample sizes visible.
- Identify stock snapshots at or below configured reorder points.
- Make source-quality issues visible and document their disposition.
- Provide reusable SQL, spreadsheet and Power BI setup materials.

## Users and decisions (assumed)
- Operations analyst: review delayed orders and cancellation patterns.
- Pharmacy operations lead: inspect pharmacy variation and replenishment candidates.
- Data analyst: refresh source files, validate joins and communicate exceptions.
- Simulated data-engineering contact: receive reproducible issue descriptions. This workflow is fictional and was not performed with an actual team.

## Scope and business rules
- Synthetic orders cover one calendar year; all identifiers and records are generated.
- A clean order has a unique key, parseable order timestamp and valid pharmacy key.
- Status values are normalized to `delivered`, `cancelled`, `returned` or `processing`.
- Fulfilment time is `delivered_ts - order_ts`; only delivered orders with both valid timestamps are eligible.
- Within-six-hour rate uses eligible delivered orders as the denominator.
- Delivered item value sums line amounts for delivered orders; it is not recognized revenue.
- Inventory at/below reorder is a flag, not an automatic purchase recommendation.
- Quarantined rows remain in raw data and issue log, not cleaned KPI outputs.

## Acceptance criteria
1. Six relational CSV entities are supplied with stable keys and documented relationships.
2. Generator recreates deterministic sample, controlled quality defects, cleaned exports, workbook and metrics.
3. Validation script exits nonzero when core key, quantity or timestamp constraints fail.
4. SQL examples demonstrate joins, CTE, subquery, conditional aggregation, window functions, elapsed-time calculations and quality checks.
5. Excel contains a formula-driven KPI summary, structured detail table and pivot-ready table; refresh instructions are included.
6. Power BI source tables, DAX measures and page layout are provided; no `.pbix` is claimed.
7. Findings state synthetic provenance, reproducible values, interpretation limits and no causal or company-specific claims.

## Out of scope
Live APIs, actual Power Query connections, native PivotTable caches, Power BI `.pbix`, prescription records, personal data, production scheduling and stakeholder approval.

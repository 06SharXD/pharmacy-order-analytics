# Pharmacy Order Fulfilment & Inventory Analytics

An end-to-end **synthetic portfolio project** demonstrating relational modeling, SQL analysis, reproducible data generation, data-quality handling, spreadsheet reporting and Power BI model planning. It contains no real PharmEasy or other company data and does not represent a real operational system.

## Quick start

Requires Python 3.10+ and `openpyxl` to regenerate the workbook. Generator, validator and analyzer otherwise use Python's standard library.

```bash
python python/generate_data.py
python python/validate.py
python python/analyze.py
python python/load_sqlite.py
python python/run_sql_examples.py
```

The generator uses seed `20261114` and recreates CSVs, planted quality issues, cleaned model, workbook and initial report. `analyze.py` independently recomputes core KPIs into `reports/metrics_recomputed.json`; `load_sqlite.py` builds a local SQLite database from cleaned CSVs. Data is for demonstration and contains no personal, prescription or company records.

## Deliverables

- `data/raw/`: orders, order items, products, inventory, pharmacies and delivery events.
- `data/cleaned/`: cleaned relational exports with documented dispositions.
- `sql/schema.sql` and `sql/business_analysis.sql`: constraints, joins, CTEs, subqueries, conditional aggregation, window functions, elapsed-time logic and data checks.
- `excel/pharmacy_operations.xlsx`: raw entity tabs, documented Power Query import/cleaning recipe, formula-based summary, Excel Table order detail, issue register and pivot-ready data. Native PivotTables and Power Query refresh connections are not embedded.
- `powerbi/`: import-ready fact CSV, DAX measure examples, relationship suggestions and four-page dashboard layout specification. No `.pbix` file is included.
- `requirements/`, `documentation/`: business brief, KPI definitions and data dictionary.
- `data_quality/`: issue register and explicitly simulated escalation workflow.
- `reports/`: reproducible metric output and interpretation-limited insights report.
- `resume/pharmeasy_data_analyst.tex`: PharmEasy-targeted resume source with project claims limited to delivered artifacts.

## Excel refresh instructions

Open `excel/pharmacy_operations.xlsx` in Excel. `Order Detail` and `Pivot Ready` are structured Excel Tables. To extend with new data, rerun the generator, replace the table body while preserving headers/table names, extend tables to the last row, then recalculate formulas. `KPI Summary` formulas reference `tblOrders`. The pivot-ready tab can be used to create a native PivotTable in Excel; this project does not ship a PivotTable cache or automated Power Query connection. Raw CSVs are source inputs; cleaned CSVs are the reporting layer.

## Power BI setup

Follow `powerbi/README.md` to import cleaned tables, set relationships, add measures and build the specified pages. The project supplies the CSV model and report specification, not an authored `.pbix` dashboard.

## Public real-world dataset alternative

The current fulfilment scenario is synthetic because the public real-world pharmacy dataset found for this project covers sales and stock movements but does not include prescription-validation, dispatch or delivery timestamps. See `documentation/public_dataset_assessment.md` for its source, CC BY 4.0 license, scope and limits. A real-data portfolio version should focus on sales and inventory; the current six-hour fulfilment results must remain explicitly synthetic.

## Limitations

No real data, live connectors, Power Query automation, native Excel PivotTables, Power BI `.pbix`, production scheduling or external stakeholder collaboration are included. Timestamp timezone behavior and data distributions are simplified for a portfolio exercise. Validate all tools and claims before describing this project in an interview.


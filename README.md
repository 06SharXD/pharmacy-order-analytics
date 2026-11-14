# Pharmacy Order Fulfilment & Inventory Analytics

This project explores how order fulfilment, cancellations and inventory could be tracked for a pharmacy delivery service. It uses generated sample records, not PharmEasy data or records from a real pharmacy.

## Run it

Requires Python 3.10 or later. Install `openpyxl` to regenerate the Excel workbook. The analysis and validation scripts use the Python standard library.

```bash
python python/generate_data.py
python python/validate.py
python python/analyze.py
python python/load_sqlite.py
python python/run_sql_examples.py
```

The generator uses a fixed seed (`20261114`) so it recreates the same CSVs, data-quality examples, workbook and report. The included files are ready to inspect without running the generator first.

## Project files

- `data/raw/` and `data/cleaned/`: generated orders, items, products, inventory, pharmacies and delivery events. The raw files contain planted quality issues; the cleaned files follow the dispositions in `data_quality/issue_register.csv`.
- `python/`: data generator, validation, analysis and SQLite loading scripts.
- `sql/`: table definitions, business queries and data-quality checks.
- `excel/pharmacy_operations.xlsx`: KPI summary, source tabs, order detail and pivot-ready data. It has no saved PivotTable cache or automated Power Query connection.
- `powerbi/`: CSV model, example DAX measures and dashboard setup notes. There is no `.pbix` file.
- `requirements/`, `documentation/`, `data_quality/` and `reports/`: project brief, field and KPI definitions, issue notes, and results.
- `resume/pharmeasy_data_analyst.tex`: the resume version used for the PharmEasy application.

## Workbook and Power BI

The workbook's `Order Detail` and `Pivot Ready` sheets are structured tables. The `KPI Summary` uses formulas based on the order table. Refresh steps are in the workbook and in the Python generator comments. The pivot-ready data can be used to make a PivotTable in Excel.

For Power BI, import the cleaned tables and `powerbi/fact_orders.csv`, then follow `powerbi/README.md` for relationships, measures and suggested report pages.

## About the data

Every record is generated for this project with no personal, prescription or company data. The dataset is included so the queries, workbook and reported numbers can be checked locally. The six-hour delivery results describe only this sample.

A public pharmacy dataset with sales and stock movements is discussed in [`documentation/public_dataset_assessment.md`](documentation/public_dataset_assessment.md). It does not include the prescription, dispatch and delivery timestamps needed for this project's fulfilment analysis, so it cannot replace the generated data for those measures.


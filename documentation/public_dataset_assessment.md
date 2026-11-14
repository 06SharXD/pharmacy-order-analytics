# Public real-world data option

**Dataset:** [IRPD: Indonesian Retail Pharmacy Sales and Stock Transaction Dataset (2023–2025), version 2](https://data.mendeley.com/datasets/w6zjtdjk9m/2), DOI [10.17632/w6zjtdjk9m.2](https://doi.org/10.17632/w6zjtdjk9m.2). It is published under CC BY 4.0. The publisher describes the source as transaction-level POS exports from one retail pharmacy in Central Java, with anonymized names. Version 2 removes patient names from free-text stock descriptions. The published files include 649,656 raw sales rows, 804,027 raw stock-movement rows, and cleaned processed versions.

## What it can support

- Sales mix, time-of-day and seasonality analysis.
- Stock movements, stock-level patterns, expiry-risk exploration, and data cleaning.
- SQL, Excel and Power BI analysis of real-world pharmacy POS/stock records.

## What it cannot support

The published fields do not provide e-commerce order lifecycle events, prescription-validation time, dispatch time, or delivery time. Therefore they cannot substantiate a prescription-to-delivery six-hour SLA, order cancellation rates for an online fulfilment service, or PharmEasy-specific outcomes. The dataset also has no cost or purchase-price fields, so cost-based margin is unavailable.

## Why the current project uses synthetic data

The portfolio project was built to demonstrate an order-to-delivery workflow with linked order, item, pharmacy, inventory and delivery-event tables. No suitable real public dataset with those full lifecycle fields was identified. We used deterministic synthetic data to make the workflow reproducible and to demonstrate SQL joins, CTEs, window functions, date/time calculations and data-quality handling without presenting invented records as company data.

For a real-data version, the project should be re-scoped to sales and stock movement analysis using IRPD. If the delivery-SLA scenario is retained, its delivery-event table and every result derived from it must remain explicitly labelled synthetic and separate from the public records. Do not merge the two populations or describe the scenario metrics as real operational findings.

## Attribution and reuse

Credit the dataset authors and cite the DOI when reusing the data. The current repository does not redistribute the dataset files; download them from Mendeley Data and follow the dataset README's processing notes. This avoids copying a large third-party archive into this repository.


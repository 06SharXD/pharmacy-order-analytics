# Simulated data-quality escalation workflow

**Simulation only.** No real issue was filed, no actual data-engineering team was contacted, and no production incident or remediation occurred.

1. Run `python python/validate.py` and inspect `issue_register.csv`.
2. Group exceptions by source, issue code, severity and refresh batch; preserve source row/key and a minimal reproducible example.
3. Estimate analytical impact (e.g. unattributable pharmacy KPI, invalid elapsed time) without inventing business impact amounts.
4. Prepare a ticket with dataset, expected rule, observed value, affected key, reproducible check, severity and proposed owner.
5. Pause only affected metric publication when the issue changes its denominator or key attribution; publish unaffected metrics with exception counts visible.
6. Re-run checks after a hypothetical fix, compare before/after counts, then document closure criteria.

The CSV issue register is a training artifact, not evidence of collaboration or a real escalation.

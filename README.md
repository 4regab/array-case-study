# Academic Analytics Lite

## Objective

Build a clean data pipeline that ingests student records, processes them with array-based operations, and outputs insights for instructors. The focus is on using arrays and modular Python design to simulate real-world analytics systems.

## Required Features

1. Clean ingest: Read CSV, validate, and handle bad rows.
2. Array operations: Select, project, sort, insert, and delete.
3. Analytics: Compute weighted grades, distributions, percentiles, outliers, and improvements.
4. Reports: Print summary, export per-section CSVs, and generate 'at-risk' lists.
5. Configuration: Load JSON config (weights, thresholds, folder paths).

## Stretch Features

- Compare sections statistically
- Implement NumPy version
- Plot histograms or box plots

## Program Structure

```
data/input.csv
src/
  ingest.py — read_csv, validate
  transform.py — compute_final, letter_grade
  analyze.py — stats, percentiles, outliers
  reports.py — print and export
  main.py — main pipeline
config.json
```

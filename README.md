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

## Prerequisites

Before running the application, ensure you have the following installed:

1. Python 3 or higher  
2. pip (Python package manager)

You also need the following Python libraries:

To install dependencies, use:
```bash
pip install numpy matplotlib
```

---

## How to Run

1. Clone this repository:
```bash
git clone https://github.com/4regab/array-case-study.git
cd array-case-study
```

2. Run the script:
```bash
cd src
python reports.py
```


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

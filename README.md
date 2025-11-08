# Academic Analytics Lite

## Objective

Build a clean data pipeline that ingests student records, processes them with array-based operations, and outputs insights for instructors. The focus is on using arrays and modular Python design to simulate real-world analytics systems.

## Features

### Required Features (All Implemented)
1. **Clean ingest**: Read CSV, validate, and handle bad rows.
2. **Array operations**: Select, project, sort, insert, and delete.
3. **Analytics**: Compute weighted grades, distributions, **percentiles**, **outliers**, and **improvements**.
4. **Reports**: Print summary, export per-section CSVs, and generate 'at-risk' lists.
5. **Configuration**: Load JSON config (weights, thresholds, folder paths).

### Stretch Features (All Implemented)
6. **Compare sections statistically** - Full section comparison with visualizations
7. **Implement NumPy version** - All analytics use NumPy array operations
8. **Plot histograms or box plots** - Multiple chart types including histograms, box plots, bar charts

### Analytics Features
- **Percentiles**: 25th, 50th, 75th, 90th, 95th percentile calculations
- **Outlier Detection**: 
  - IQR (Interquartile Range) method
  - Z-score method (3 standard deviations)
- **Improvement Tracking**:
  - Most improved students (quiz avg to final exam)
  - Declining performance detection
  - Improvement percentage calculations

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3 or higher  

## How to Run

1. Clone this repository:
```bash
git clone https://github.com/4regab/array-case-study.git
cd array-case-study
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit web application:
```bash
cd src
streamlit run main.py
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

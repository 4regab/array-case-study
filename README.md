# Academic Analytics Lite

A clean data pipeline that ingests student records, processes them with array-based operations, and outputs insights for instructors. Built using arrays and modular Python design to simulate real-world analytics systems. Features an interactive Streamlit web interface for data visualization and analysis.

## Features

### Required Features (All Implemented)
1. **Clean ingest**: Read CSV, validate, and handle bad rows.
2. **Array operations**: Select, project, sort, insert, and delete.
3. **Analytics**: Compute weighted grades, distributions, **percentiles**, **outliers**, and **improvements**.
4. **Reports**: Print summary, export per-section CSVs, and generate 'at-risk' lists.
5. **Configuration**: Load JSON config (weights, thresholds, folder paths).

### Implemented Stretch Features 
6. **Compare sections statistically** - Full section comparison with visualizations
7. **Implement NumPy version** - All analytics use NumPy array operations
8. **Plot histograms or box plots** - Multiple chart types including histograms, box plots, bar charts


## Data Model

The system uses arrays of dictionaries to represent student records.

**CSV Columns**:
- `student_id`, `last_name`, `first_name`, `section`
- `quiz1` to `quiz5`, `midterm`, `final`, `attendance_percent`

**Parsing Rules**:
- Missing numeric fields default to `None`
- Trim spaces in names and sections
- Scores are validated to be from 0 to 100 only

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.8 or higher

## How to Use

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

The application will open in your default web browser at `http://localhost:8501`

## Program Structure

```
array-case-study/
├── data/
│   ├── input.csv           # Sample student data
│   └── output/             # Generated reports and csv files
├── src/
│   ├── ingest.py          # CSV reading and validation
│   ├── transform.py       # Grade computation and transformations
│   ├── analyze.py         # Statistical analysis and visualizations
│   ├── reports.py         # Report generation and exports
│   └── main.py            # Main Streamlit application
├── config.json            # Configuration (weights, thresholds, paths)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration

The `config.json` file controls the application behavior:

**Weights**:
- Quizzes: 30%
- Midterm: 30%
- Final: 30%
- Attendance: 10%

**Grade Scale**:
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: 0-59

**Thresholds**:
- At-risk threshold: 60 (students below this grade)

**Paths**:
- Input CSV: `../data/input.csv`
- Output folder: `../data/output`

You can modify these values to customize the grading system.

## Report Outputs

The application generates the following reports in the `data/output/` folder:

1. **Summary Report** (`summary_report.txt`) - Overall statistics and grade distribution
2. **Section Reports** (`section_X.csv`) - Individual CSV files per section
3. **At-Risk Students** (`at_risk_students.csv`) - Students below the threshold
4. **Visualizations** - Multiple PNG charts (grade distribution, percentiles, outliers, etc.)

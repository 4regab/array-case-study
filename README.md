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

## Complexity Discussion

This project uses several Python libraries to handle data work, analysis, and charts:

**NumPy** helps with fast math operations on student data. The project uses NumPy arrays to calculate averages, medians, and percentiles quickly. It finds unusual scores using the IQR method and processes all student records at once without slow loops. Using NumPy instead of regular Python lists makes the program much faster, especially with many students. Tasks that need multiple loops in basic Python are done in one step with NumPy.

**Pandas** makes filtering and selecting data easier, groups data by section for comparisons, and handles missing scores cleanly. Pandas DataFrames make complex data changes simpler while working well with the array-based design.The main data uses arrays of dictionaries to show basic data structures. 

**Matplotlib** creates all the charts in the program. It makes grade distribution charts, box plots that show unusual scores, bar charts for letter grades and quiz results, and comparison charts for different sections. Each chart is saved as a PNG file for reports and presentations. The charts turn numbers into easy-to-read pictures.

**Streamlit** turns the program into a web app that anyone can use in their browser. It shows charts that update right away, has forms to add or delete student records, and displays new charts without reloading the page. It also lets users download reports and CSV files. It makes building web apps simple without needing to learn complex web tools.


## Data Model

The system uses arrays of dictionaries to represent student records.

**CSV Columns**:
- `student_id`, `last_name`, `first_name`, `section`
- `quiz1` to `quiz5`, `midterm`, `final`, `attendance_percent`

**Parsing Rules**:
- Missing numeric fields default to `None`
- Trim spaces in names and sections
- Scores are validated to be from 0 to 100 only

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


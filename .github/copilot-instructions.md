# AI Agent Instructions for Academic Analytics Lite

This document outlines key patterns and conventions for working with this academic data pipeline project.

## Project Architecture

The project follows a modular data pipeline architecture with clear component boundaries:

1. **Data Ingestion** (`src/ingest.py`): 
   - Handles CSV file reading and data validation
   - Key function: `ingest(filename='input.csv')` validates student records
   - Score validation enforces 0-100 range

2. **Data Transformation** (`src/transform.py`):
   - Applies weights and calculations to raw data
   - Configuration driven via `config.json` (weights, thresholds, paths)
   - Key function: `compute_final()` calculates weighted grades

3. **Analysis** (`src/analyze.py`):
   - `StudentAnalytics` class handles statistical computations
   - Uses NumPy for core statistics and Matplotlib for visualizations
   - Supports section comparison and grade distribution analysis

4. **Reporting** (`src/reports.py`):
   - `ReportGenerator` class creates summary and detailed reports
   - Generates at-risk student lists based on configurable thresholds
   - CSV exports organized by section

## Development Workflows

1. **Setup**:
   ```bash
   pip install numpy matplotlib
   ```

2. **Running the Pipeline**:
   - Entry point: `python src/reports.py`
   - Input data expected in `data/input.csv`
   - Outputs saved to `data/output/`

3. **Configuration**:
   - All configurable values in `config.json`
   - Key sections: weights, thresholds, grade_scale, paths
   - Example weight modification:
   ```json
   "weights": {
       "quizzes": 0.3,
       "midterm": 0.3,
       "final": 0.3,
       "attendance": 0.1
   }
   ```

## Project-Specific Conventions

1. **Data Structure**:
   - Student records as dictionaries with standardized keys
   - Quiz scores named as `quiz1` through `quiz5`
   - Missing/invalid scores stored as `None`

2. **Error Handling**:
   - Validation failures return `None` instead of raising exceptions
   - File path errors raise `FileNotFoundError`

3. **Dependencies**:
   - Core analysis requires NumPy
   - Visualization features need Matplotlib
   - No other external dependencies

## Integration Points

1. **Input Data Format**:
   - CSV with headers: last_name, first_name, section, quiz1-5, midterm, final, attendance
   - Values must be numeric 0-100 or empty

2. **Output Formats**:
   - Text-based summary reports
   - Section-specific CSV exports
   - Optional visualization plots
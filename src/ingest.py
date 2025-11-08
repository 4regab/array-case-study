import csv
import os


def read_csv(filename='input.csv'):  # Load student data from CSV file in data folder
    script_dir = os.path.dirname(
        os.path.abspath(__file__))  # Get script directory
    # Build path to data folder
    filepath = os.path.join(script_dir, '..', 'data', filename)
    filepath = os.path.normpath(filepath)  # Normalize path for Windows/Linux

    if not os.path.exists(filepath):  # Check if file exists
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    students = []

    with open(filepath, 'r', encoding='utf-8') as file:  # Open CSV file
        reader = csv.DictReader(file)  # Read as dictionary with headers
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        for row in reader:  # Loop through each row
            student = {}
            for key, value in row.items():  # Process each column
                key = key.strip()
                if key in ['last_name', 'first_name', 'section']:  # Text fields
                    student[key] = value.strip()
                elif key in ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5',  # Numeric scores
                             'midterm', 'final', 'attendance_percent']:
                    student[key] = validate_score(value)
                elif key == 'student_id':  # Student ID
                    student[key] = value.strip() if value else None
            students.append(student)

    return students


def validate_score(value):  # Validate score is between 0-100, return None if invalid
    if not value or value.strip() == '':  # Empty value
        return None

    try:
        score = float(value)  # Convert to number
        return score if 0 <= score <= 100 else None  # Check range
    except ValueError:  # Not a number
        return None

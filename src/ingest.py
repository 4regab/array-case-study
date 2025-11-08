import csv
import os

# Read student data from CSV file


def read_csv(filename='input.csv'):
    filepath = os.path.join('..', 'data', filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filename}")
    students = []

    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        for row in reader:
            student = {}
            for key, value in row.items():
                key = key.strip()
                if key in ['last_name', 'first_name', 'section']:
                    student[key] = value.strip()
                elif key in ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5',
                             'midterm', 'final', 'attendance_percent']:
                    student[key] = validate_score(value)
                elif key == 'student_id':
                    student[key] = value.strip() if value else None
            students.append(student)

    return students

# Validate score is between 0-100, return None if invalid


def validate_score(value):
    if not value or value.strip() == '':
        return None

    try:
        score = float(value)
        return score if 0 <= score <= 100 else None
    except ValueError:
        return None

import csv
import os

# Handles input csv file path detection (works from data folder)


def find_csv_file(filename):
    """Find CSV file in multiple possible locations."""
    # List of possible paths to check
    possible_paths = [
        filename,  # Current directory
        os.path.join('data', filename),  # data/ folder (from root)
        os.path.join('..', 'data', filename),
    ]

    # Check each path
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # If not found in any location, raise an error
    raise FileNotFoundError(f"CSV file not found: {filename}")


# Validate scores from 0 to 100 only, it will return a number or none
def validate_score(value):
    """Validate and convert score to float (0-100 range)."""
    # Empty value then it will return none
    if not value or value.strip() == '':
        return None
    # Convert score into float if valid, else will return None
    try:
        score = float(value)
        if 0 <= score <= 100:
            return score
        return None
    except ValueError:
        return None


# Reads student data from CSV file
def ingest(filename='input.csv'):
    """Read and process student data from CSV file."""
    filepath = find_csv_file(filename)

    student_records = []  # Array to store student records

    # To open and read CSV file
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty")

        # Process each row
        for row in reader:
            student = {}

            # Process each column
            for key, value in row.items():
                key = key.strip()  # This removes spaces from column name

                # Name and Section, and trim spaces
                if key in ['last_name', 'first_name', 'section']:
                    student[key] = value.strip()

                # Scores - validate 0-100
                elif key in [
                    'quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5',
                    'midterm', 'final', 'attendance_percent'
                ]:
                    student[key] = validate_score(value)

                # The Student ID - keep as string and trim spaces
                elif key == 'student_id':
                    student[key] = value.strip() if value else None

            # Add student to list
            student_records.append(student)

    # Return list of students
    return student_records


# print the result.
if __name__ == '__main__':
    students = ingest()
    print(students)

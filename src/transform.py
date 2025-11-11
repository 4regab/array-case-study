from typing import List, Dict, Any, Optional
import json
import pandas as pd
import os


# Load config from JSON file
def load_config(config_path: str = '../config.json') -> Dict[str, Any]:
    script_dir = os.path.dirname(
        os.path.abspath(__file__))  # Get script directory
    full_path = os.path.join(script_dir, config_path)  # Build path to config
    full_path = os.path.normpath(full_path)  # Normalize path

    with open(full_path, 'r') as f:
        return json.load(f)  # Parse and return JSON config


# Filter students by condition (like SQL WHERE)
def select_students(students: List[Dict[str, Any]], condition: callable) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)  # Convert to DataFrame
    mask = df.apply(condition, axis=1)  # Apply condition to each row
    return df[mask].to_dict('records')  # Return filtered students


# Select specific fields (like SQL SELECT columns)
def project_students(students: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)  # Convert to DataFrame
    # Filter to existing fields
    available_fields = [f for f in fields if f in df.columns]
    # Return with only requested fields
    return df[available_fields].to_dict('records')


# Add one student and recalculate grades
def insert_student(students: List[Dict[str, Any]], new_student: Dict[str, Any]) -> List[Dict[str, Any]]:
    students_copy = students.copy()  # Copy to avoid modifying original
    students_copy.append(new_student)  # Add new student
    return transform_students(students_copy)  # Recalculate all grades


# Add multiple students at once
def insert_students_bulk(students: List[Dict[str, Any]], new_students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not new_students:
        return students
    df_existing = pd.DataFrame(
        students) if students else pd.DataFrame()  # Existing students
    df_new = pd.DataFrame(new_students)  # New students
    df_combined = pd.concat([df_existing, df_new],
                            ignore_index=True)  # Combine both
    # Recalculate grades
    return transform_students(df_combined.to_dict('records'))


# Remove student by ID
def delete_student(students: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)  # Convert to DataFrame
    # Filter out the student
    return df[df['student_id'] != student_id].to_dict('records')


# Calculate quiz avg, final grade, letter grade
def transform_students(student_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not student_records:
        return []

    config = load_config()  # Load config
    # Grade weights (quiz, midterm, final, attendance)
    weights = config['weights']
    scale = config['grade_scale']  # Letter grade scale (A, B, C, D thresholds)

    for student in student_records:  # Process each student
        # Get all 5 quiz scores
        quiz_scores = [student.get(f'quiz{i}') for i in range(1, 6)]
        # Ignore missing quizzes
        valid_quizzes = [q for q in quiz_scores if q is not None]
        student['quiz_avg'] = sum(
            # Calculate average
            valid_quizzes) / len(valid_quizzes) if valid_quizzes else None

        quiz_avg = student.get('quiz_avg')  # Get components for final grade
        midterm = student.get('midterm')
        final_exam = student.get('final')
        attendance = student.get('attendance_percent')

        if None in [quiz_avg, midterm, final_exam, attendance]:  # Missing data
            student['final_grade'] = None
            student['letter_grade'] = 'N/A'
        else:  # Calculate weighted final grade
            final_grade = (quiz_avg * weights['quizzes'] + midterm * weights['midterm'] +
                           final_exam * weights['final'] + attendance * weights['attendance'])
            student['final_grade'] = final_grade

            if final_grade >= scale['A']:  # Determine letter grade
                student['letter_grade'] = 'A'
            elif final_grade >= scale['B']:
                student['letter_grade'] = 'B'
            elif final_grade >= scale['C']:
                student['letter_grade'] = 'C'
            elif final_grade >= scale['D']:
                student['letter_grade'] = 'D'
            else:
                student['letter_grade'] = 'F'

    return student_records


# Sort students by any field
def sort_students(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)  # Convert to DataFrame
    # Sort (missing values last)
    df_sorted = df.sort_values(
        by=key, ascending=not reverse, na_position='last')
    return df_sorted.to_dict('records')  # Return sorted list


# Get top N students by grade
def get_top_performers(students: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)  # Convert to DataFrame
    # Remove students with missing grades
    df_with_grades = df[df['final_grade'].notna()]
    df_sorted = df_with_grades.sort_values(
        by='final_grade', ascending=False)  # Sort highest first
    return df_sorted.head(top_n).to_dict('records')  # Return top N


# Get students below threshold
def get_at_risk_students(students: List[Dict[str, Any]], threshold: Optional[float] = None) -> List[Dict[str, Any]]:
    if not students:
        return []
    if threshold is None:  # Use config threshold if not provided
        threshold = load_config().get('thresholds', {}).get('at_risk', 60)

    df = pd.DataFrame(students)  # Convert to DataFrame
    at_risk_df = df[(df['final_grade'].notna()) & (
        df['final_grade'] < threshold)]  # Filter below threshold
    at_risk_sorted = at_risk_df.sort_values(
        by='final_grade', ascending=True)  # Sort lowest first
    return at_risk_sorted.to_dict('records')  # Return at-risk students

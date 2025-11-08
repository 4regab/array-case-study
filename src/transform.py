from typing import List, Dict, Any, Optional
import json
import pandas as pd
import numpy as np


# Load configuration from config.json file in the root folder
def load_config(config_path: str = '../config.json') -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return json.load(f)

# SELECT: Filter students based on conditions (WHERE clause)
# SELECT operation - Filter students based on a condition function.
# Example: select_students(students, lambda s: s['final_grade'] > 90)


def select_students(students: List[Dict[str, Any]], condition: callable) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)
    mask = df.apply(condition, axis=1)
    return df[mask].to_dict('records')


# PROJECT: Select specific columns/fields from students
# PROJECT operation - Select only specific fields from student records.
# Example: project_students(students, ['student_id', 'first_name', 'final_grade'])
def project_students(students: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)
    available_fields = [f for f in fields if f in df.columns]
    return df[available_fields].to_dict('records')


# INSERT: Add new student(s) to the array
# INSERT operation - Add a new student to the array and recalculate grades.
def insert_student(students: List[Dict[str, Any]], new_student: Dict[str, Any]) -> List[Dict[str, Any]]:
    students_copy = students.copy()
    students_copy.append(new_student)
    return transform_students(students_copy)


# INSERT operation (bulk) - Add multiple students at once using pandas concat.
def insert_students_bulk(students: List[Dict[str, Any]], new_students: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not new_students:
        return students

    df_existing = pd.DataFrame(students) if students else pd.DataFrame()
    df_new = pd.DataFrame(new_students)
    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    return transform_students(df_combined.to_dict('records'))


# DELETE: Remove student(s) from the array
# DELETE operation - Remove a student by ID using pandas filtering.
def delete_student(students: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)
    return df[df['student_id'] != student_id].to_dict('records')


# Add computed fields to student records
def transform_students(student_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not student_records:
        return []

    config = load_config()
    weights = config['weights']
    scale = config['grade_scale']

    # Calculate quiz average and final grades for each student
    for student in student_records:
        # Calculate quiz average
        quiz_scores = [student.get(f'quiz{i}') for i in range(1, 6)]
        valid_quizzes = [q for q in quiz_scores if q is not None]
        student['quiz_avg'] = sum(valid_quizzes) / \
            len(valid_quizzes) if valid_quizzes else None

        # Calculate final grade
        quiz_avg = student.get('quiz_avg')
        midterm = student.get('midterm')
        final_exam = student.get('final')
        attendance = student.get('attendance_percent')

        if None in [quiz_avg, midterm, final_exam, attendance]:
            student['final_grade'] = None
            student['letter_grade'] = 'N/A'
        else:
            # Calculate weighted final grade
            final_grade = (
                quiz_avg * weights['quizzes'] +
                midterm * weights['midterm'] +
                final_exam * weights['final'] +
                attendance * weights['attendance']
            )
            student['final_grade'] = final_grade

            # Determine letter grade
            if final_grade >= scale['A']:
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


# Sort students by a field using pandas
def sort_students(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)
    df_sorted = df.sort_values(
        by=key, ascending=not reverse, na_position='last')
    return df_sorted.to_dict('records')


# Get top N students by final grade using pandas
def get_top_performers(students: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    if not students:
        return []
    df = pd.DataFrame(students)
    df_with_grades = df[df['final_grade'].notna()]
    df_sorted = df_with_grades.sort_values(by='final_grade', ascending=False)
    return df_sorted.head(top_n).to_dict('records')


# Get students below threshold using pandas
def get_at_risk_students(students: List[Dict[str, Any]], threshold: Optional[float] = None) -> List[Dict[str, Any]]:
    if not students:
        return []
    if threshold is None:
        threshold = load_config().get('thresholds', {}).get('at_risk', 60)

    df = pd.DataFrame(students)
    at_risk_df = df[(df['final_grade'].notna()) &
                    (df['final_grade'] < threshold)]
    at_risk_sorted = at_risk_df.sort_values(by='final_grade', ascending=True)
    return at_risk_sorted.to_dict('records')

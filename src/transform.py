from typing import List, Dict, Any, Optional
import json
import os


def load_config(config_path: str = '../config.json') -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return json.load(f)


config = load_config()

# Computes the weighted final grade


def compute_final(quiz_avg: Optional[float], midterm: Optional[float], final: Optional[float], attendance: Optional[float]) -> Optional[float]:
    if quiz_avg is None or midterm is None or final is None or attendance is None:
        return None
    weights = config['weights']
    return (quiz_avg * weights['quizzes'] +
            midterm * weights['midterm'] +
            final * weights['final'] +
            attendance * weights['attendance'])

# Converts numeric grade to letter grade \


def letter_grade(grade: Optional[float]) -> str:
    if grade is None:
        return None
    scale = config['grade_scale']
    if grade >= scale['A']:
        return 'A'
    elif grade >= scale['B']:
        return 'B'
    elif grade >= scale['C']:
        return 'C'
    elif grade >= scale['D']:
        return 'D'
    else:
        return 'F'


def transform_students(student_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for student in student_records:
        # Compute quiz_avg: Average of quiz1 to quiz5,
        quizzes = [student.get(f'quiz{i}') for i in range(
            1, 6) if student.get(f'quiz{i}') is not None]
        student['quiz_avg'] = sum(quizzes) / len(quizzes) if quizzes else None

        quiz_avg = student['quiz_avg']
        midterm = student.get('midterm')
        final = student.get('final')
        attendance = student.get('attendance_percent')
        student['final_grade'] = compute_final(
            quiz_avg, midterm, final, attendance)

        # Compute letter_grade based on final_grade
        student['letter_grade'] = letter_grade(student['final_grade'])

    return student_records


def select(students: List[Dict[str, Any]], condition) -> List[Dict[str, Any]]:
    # Filter students based on condition function
    return [s for s in students if condition(s)]


def project(students: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
   # Extract only specified fields from students
    return [{field: s.get(field) for field in fields} for s in students]


def sort_students(students: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    # Sort students by a field in-place
    students.sort(key=lambda s: s.get(key) if s.get(key)
                  is not None else -1, reverse=reverse)
    return students


def insert_student(students: List[Dict[str, Any]], student: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Insert a new student record
    students.append(student)
    return students


def delete_student(students: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
    # Delete student by student_id in-place
    for i, s in enumerate(students):
        if s.get('student_id') == student_id:
            students.pop(i)
            break
    return students

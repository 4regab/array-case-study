from typing import List, Dict, Any, Optional
import json
import os
from ingest import ingest  

def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
       
        return {
            "weights": {
                "quizzes": 0.3,
                "midterm": 0.3,
                "final": 0.3,
                "attendance": 0.1
            },
            "max_scores": {
                "quiz1": 100,
                "quiz2": 100,
                "midterm": 100,
                "final": 100,
                "attendance": 100
            },
            "thresholds": {
                "at_risk": 60
            },
            "grade_scale": {
                "A": 90,
                "B": 80,
                "C": 70,
                "D": 60,
                "F": 0
            },
            "path": {
                "input_csv": "data/input.csv",
                "output_folder": "data/output"
            }
        }

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
        return 'N/A'
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
        quizzes = [student.get(f'quiz{i}') for i in range(1, 6) if student.get(f'quiz{i}') is not None]
        student['quiz_avg'] = sum(quizzes) / len(quizzes) if quizzes else None
        
        quiz_avg = student['quiz_avg']
        midterm = student.get('midterm')
        final = student.get('final')
        attendance = student.get('attendance_percent')
        student['final_grade'] = compute_final(quiz_avg, midterm, final, attendance)
        
        # Compute letter_grade based on final_grade
        student['letter_grade'] = letter_grade(student['final_grade'])
    
    return student_records

# Main execution block
if __name__ == '__main__':
    # Ingest the data from the path in config
    students = ingest(config['path']['input_csv'])
    
    # Transform the data
    transformed_students = transform_students(students)
    
    # Print the transformed records
    print(transformed_students)

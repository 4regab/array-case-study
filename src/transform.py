from ingest import ingest

def compute_final(quiz_avg, midterm, final, attendance):
    # If any required component is None, return None
    if quiz_avg is None or midterm is None or final is None or attendance is None:
        return None
    
    # Calculate weighted grade
    weighted_quiz = quiz_avg * 0.3
    weighted_midterm = midterm * 0.3
    weighted_final = final * 0.3
    weighted_attendance = attendance * 0.1
    
    return weighted_quiz + weighted_midterm + weighted_final + weighted_attendance

def letter_grade(grade):
    if grade is None:
        return 'N/A'
    elif grade >= 90:
        return 'A'
    elif grade >= 80:
        return 'B'
    elif grade >= 70:
        return 'C'
    elif grade >= 60:
        return 'D'
    else:
        return 'F'

# Main transform function: Adds computed fields to all records
def transform_students(student_records):
    for student in student_records:
        # Compute quiz_avg: Average of quiz1 to quiz5, ignoring None values
        quizzes = [student.get(f'quiz{i}') for i in range(1, 6) if student.get(f'quiz{i}') is not None]
        if quizzes:
            student['quiz_avg'] = sum(quizzes) / len(quizzes)
        else:
            student['quiz_avg'] = None
        
        # Compute final_grade using the weighted formula
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
    # Ingest the data
    students = ingest()
    
    # Transform the data
    transformed_students = transform_students(students)
    
    # Print the transformed records
    print(transformed_students)

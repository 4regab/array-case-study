import csv
import os 

# Handles input csv file path detection (works from src/ or root directory)
def find_csv_file(filename):
    # Check if the CSV file exists in the current folder or root directory
    if os.path.exists(filename):
        return filename
    # If not found in the root directory, check inside the src folder
    src_path = os.path.join('src', filename)
    if os.path.exists(src_path):  
        return src_path
    # If still not found in both location, it will raise an error
    raise FileNotFoundError(f"CSV file not found: {filename}")     


# Validate scores from 0 to 100 only, it will return a number or none
def validate_score(value): 
    # Empty value then it will return none
    if not value or value.strip() == '':
        return None 
    # Convert score into float if valid, else will return None
    try: 
        score = float(value)
        if 0 <= score <= 100: 
            return score
        else: 
            return None 
    except ValueError: 
        return None 

        
# Reads student data from CSV file           
def ingest(filename='input.csv'):
    filepath = find_csv_file(filename)
    
    students = []  # Array to store student records
    
    # To open and read CSV file
    with open(filepath, 'r') as file: 
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise Exception("CSV file is empty")
        
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
                elif key in ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'midterm', 'final', 'attendance_percent']:
                    student[key] = validate_score(value) 
                
                # The Student ID convert to number
                elif key == 'student_id':    
                    try:
                        student[key] = int(value)
                    except:
                        student[key] = None
            
            # Add student to list
            students.append(student)
    
    # Return list of students
    return students

#to view the output of this code 
if __name__ == '__main__':
    print("✅ ingest.py is running correctly!")
    students = ingest()
    print(students)
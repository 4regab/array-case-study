import streamlit as st  # Web app framework
import pandas as pd  # DataFrame for displaying student data tables
import matplotlib.pyplot as plt  # Plotting library (used by chart functions)
from io import StringIO  # Convert uploaded CSV string to file-like object
import csv  # Parse CSV data from uploaded files
import os  # File system operations

# Import existing modules
from ingest import read_csv, validate_score  # Load and validate student data
# Data transformation and filtering
from transform import (transform_students, load_config, get_top_performers, get_at_risk_students, sort_students,
                       select_students, project_students,
                       insert_student, insert_students_bulk, delete_student)
from analyze import (StudentAnalytics, create_grade_distribution_chart, create_letter_grades_chart,
                     create_quiz_performance_chart, create_boxplot_chart,
                     create_section_comparison_chart, create_percentiles_chart,
                     # Analytics and chart generation
                     create_outliers_chart, create_most_improved_chart)
from reports import ReportGenerator  # Generate text summary reports

# Page config
st.set_page_config(page_title="Academic Analytics Lite", layout="wide")

# Initialize session state and load default data from input.csv
if 'students' not in st.session_state:
    st.session_state.students = transform_students(read_csv())
if 'config' not in st.session_state:
    st.session_state.config = load_config()


def csv_to_students(csv_content):
    students = []
    reader = csv.DictReader(StringIO(csv_content))
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
    # Use insert_students_bulk for array operation
    return insert_students_bulk([], students)


def students_to_dataframe(students):
    if not students:
        return pd.DataFrame()
    df_data = []
    for s in students:
        df_data.append({
            'Student ID': str(s.get('student_id', '')),
            'Last Name': s.get('last_name', ''),
            'First Name': s.get('first_name', ''),
            'Section': s.get('section', ''),
            'Quiz 1': s.get('quiz1', ''),
            'Quiz 2': s.get('quiz2', ''),
            'Quiz 3': s.get('quiz3', ''),
            'Quiz 4': s.get('quiz4', ''),
            'Quiz 5': s.get('quiz5', ''),
            'Midterm': s.get('midterm', ''),
            'Final': s.get('final', ''),
            'Attendance %': s.get('attendance_percent', ''),
            'Final Grade': round(s.get('final_grade', 0), 2) if s.get('final_grade') else '',
            'Letter': s.get('letter_grade', '')
        })
    return pd.DataFrame(df_data)


# Sidebar with config, upload, and export
with st.sidebar:
    st.header("Config")
    weights = st.session_state.config['weights']
    at_risk_threshold = st.session_state.config.get(
        'thresholds', {}).get('at_risk', 60)
    st.caption(
        f"**Weights:** Quiz {weights['quizzes']*100:.0f}% | Mid {weights['midterm']*100:.0f}% | Final {weights['final']*100:.0f}% | Attendance {weights['attendance']*100:.0f}%")
    st.caption(f"**At-Risk:** Below {at_risk_threshold} (Grade F)")

    # File Upload
    st.subheader("Upload CSV")
    uploaded_file = st.file_uploader(
        "Upload CSV", type=['csv'], label_visibility="collapsed")
    if uploaded_file is not None:
        csv_content = uploaded_file.getvalue().decode('utf-8')
        st.session_state.students = csv_to_students(csv_content)
        st.success(f"Loaded {len(st.session_state.students)} students!")
        st.rerun()

    # Export Section
    st.subheader("Export Data")

    # At-risk students export
    at_risk_students = get_at_risk_students(st.session_state.students, 60.0)
    if at_risk_students:
        at_risk_csv = students_to_dataframe(
            at_risk_students).to_csv(index=False)

        # Save to output folder
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir_sidebar = os.path.normpath(
            os.path.join(script_dir, '..', 'data', 'output'))
        os.makedirs(output_dir_sidebar, exist_ok=True)
        with open(os.path.join(output_dir_sidebar, 'at_risk_students.csv'), 'w') as f:
            f.write(at_risk_csv)

        st.download_button(
            label="At-Risk Students CSV",
            data=at_risk_csv,
            file_name="at_risk_students.csv",
            mime="text/csv",
            key="download_at_risk",
            use_container_width=True
        )

    # Section exports
    sections = sorted(set(s.get('section')
                      for s in st.session_state.students if s.get('section')))
    if sections:
        for section in sections:
            section_students = [
                s for s in st.session_state.students if s.get('section') == section]
            section_df = students_to_dataframe(section_students)
            csv_data = section_df.to_csv(index=False)

            # Save to output folder
            with open(os.path.join(output_dir_sidebar, f'section_{section}.csv'), 'w') as f:
                f.write(csv_data)

            st.download_button(
                label=f"Section {section} CSV",
                data=csv_data,
                file_name=f"section_{section}.csv",
                mime="text/csv",
                key=f"download_section_{section}",
                use_container_width=True
            )

# Main title
st.title("Academic Analytics Lite")

# Create output directory
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.normpath(os.path.join(script_dir, '..', 'data', 'output'))
os.makedirs(output_dir, exist_ok=True)

# Summary Report
st.subheader("Summary Report")
generator = ReportGenerator(st.session_state.students, st.session_state.config)
summary = generator.generate_summary_report()
st.text(summary)

# Save summary report to file
with open(os.path.join(output_dir, 'summary_report.txt'), 'w') as f:
    f.write(summary)

# Display current data (collapsible)
with st.expander("Current Student Data", expanded=False):
    df = students_to_dataframe(st.session_state.students)
    st.dataframe(df, width='stretch')

# Add new student (collapsible)
with st.expander("Add New Student"):
    with st.form("add_student_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            student_id = st.text_input("Student ID")
            last_name = st.text_input("Last Name")
            first_name = st.text_input("First Name")
            section = st.text_input("Section")

        with col2:
            quiz1 = st.number_input("Quiz 1", 0.0, 100.0, 0.0)
            quiz2 = st.number_input("Quiz 2", 0.0, 100.0, 0.0)
            quiz3 = st.number_input("Quiz 3", 0.0, 100.0, 0.0)
            quiz4 = st.number_input("Quiz 4", 0.0, 100.0, 0.0)
            quiz5 = st.number_input("Quiz 5", 0.0, 100.0, 0.0)

        with col3:
            midterm = st.number_input("Midterm", 0.0, 100.0, 0.0)
            final = st.number_input("Final", 0.0, 100.0, 0.0)
            attendance = st.number_input("Attendance %", 0.0, 100.0, 0.0)

        submitted = st.form_submit_button("Add Student")

        if submitted:
            new_student = {
                'student_id': student_id,
                'last_name': last_name,
                'first_name': first_name,
                'section': section,
                'quiz1': quiz1,
                'quiz2': quiz2,
                'quiz3': quiz3,
                'quiz4': quiz4,
                'quiz5': quiz5,
                'midterm': midterm,
                'final': final,
                'attendance_percent': attendance
            }

            # Use insert_student array operation
            st.session_state.students = insert_student(
                st.session_state.students, new_student)
            st.success(f"Added {first_name} {last_name}!")
            st.rerun()

# Delete student
with st.expander("Delete Student"):
    student_names = [f"{s.get('student_id', '')} - {s.get('first_name', '')} {s.get('last_name', '')}"
                     for s in st.session_state.students]

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_student = st.selectbox(
            "Select student", student_names, label_visibility="collapsed")
    with col2:
        if st.button("Delete", type="primary"):
            selected_id = selected_student.split(' - ')[0]
            # Use delete_student array operation
            st.session_state.students = delete_student(
                st.session_state.students, selected_id)
            st.success(f"Deleted {selected_id}!")
            st.rerun()

# Analytics section
st.header("Analytics & Visualizations")

analytics = StudentAnalytics(st.session_state.students)

# Summary statistics
st.subheader("Summary Statistics")
stats = analytics.get_final_grade_statistics()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean", f"{stats.get('mean', 0):.2f}")
col2.metric("Median", f"{stats.get('median', 0):.2f}")
col3.metric("Std Dev", f"{stats.get('std_dev', 0):.2f}")
col4.metric("Range", f"{stats.get('range', 0):.2f}")


col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Grade Distribution")
    fig = create_grade_distribution_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'grade_distribution.png'),
                    dpi=150, bbox_inches='tight')

with col2:
    st.subheader("Letter Grades")
    fig = create_letter_grades_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'letter_grades.png'),
                    dpi=150, bbox_inches='tight')

with col3:
    st.subheader("Quiz Performance")
    fig = create_quiz_performance_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'quiz_performance.png'),
                    dpi=150, bbox_inches='tight')


# Additional Analytics Visualizations
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Grade Percentiles")
    fig = create_percentiles_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'grade_percentiles.png'),
                    dpi=150, bbox_inches='tight')

with col2:
    st.subheader("Outlier Detection")
    fig = create_outliers_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'outlier_detection.png'),
                    dpi=150, bbox_inches='tight')

with col3:
    st.subheader("Students Improvement")
    fig = create_most_improved_chart(st.session_state.students)
    if fig:
        st.pyplot(fig)
        fig.savefig(os.path.join(output_dir, 'most_improved.png'),
                    dpi=150, bbox_inches='tight')

# Section Comparison gets its own full-width row
fig = create_section_comparison_chart(st.session_state.students)
if fig:
    st.pyplot(fig)
    fig.savefig(os.path.join(output_dir, 'section_comparison.png'),
                dpi=150, bbox_inches='tight')

# Top Performers Table
st.subheader("Top Performers")

# Use select_students array operation to filter for A grade students
a_grade_students = select_students(
    st.session_state.students, lambda s: s.get('letter_grade') == 'A')
top_performers = sort_students(a_grade_students, 'final_grade', reverse=True)
top_df = students_to_dataframe(top_performers)
st.dataframe(top_df, width='stretch')

# At-Risk Students Table
st.subheader("At-Risk Students")
at_risk = get_at_risk_students(st.session_state.students, 60.0)
risk_df = students_to_dataframe(at_risk)
st.dataframe(risk_df, width='stretch')

# Section Comparison Tables
st.subheader("Section Comparison")
section_stats = analytics.get_section_comparison()

if section_stats and len(section_stats) > 0:
    section_data = []
    for section, data in sorted(section_stats.items()):
        stats = data['statistics']
        letter_dist = data['letter_grades']

        section_data.append({
            'Section': section,
            'Students': data['count'],
            'Mean': round(stats['mean'], 2),
            'Median': round(stats['median'], 2),
            'Std Dev': round(stats['std_dev'], 2),
            'Min': round(stats['min'], 2),
            'Max': round(stats['max'], 2),
            'A': letter_dist.get('A', 0),
            'B': letter_dist.get('B', 0),
            'C': letter_dist.get('C', 0),
            'D': letter_dist.get('D', 0),
            'F': letter_dist.get('F', 0)
        })

    section_df = pd.DataFrame(section_data)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("**Performance Metrics**")
        st.dataframe(section_df[['Section', 'Students', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']],
                     width='stretch', hide_index=True)

    with col2:
        st.write("**Grade Distribution**")
        st.dataframe(section_df[['Section', 'A', 'B', 'C', 'D', 'F']],
                     width='stretch', hide_index=True)
else:
    st.info("No section data available")

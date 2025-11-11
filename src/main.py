import streamlit as st  # Web app framework for creating interactive dashboards
import pandas as pd  # DataFrame library for displaying student data in tables
import os  # File system operations for creating folders and saving files

# Import existing modules from our project
from ingest import read_csv  # Load and validate student data from CSV file
# Data transformation and filtering functions
from transform import (transform_students, load_config, get_top_performers, get_at_risk_students, sort_students,
                       select_students, project_students,
                       insert_student, delete_student)
# Analytics and chart generation functions
from analyze import (StudentAnalytics, create_grade_distribution_chart, create_letter_grades_chart,
                     create_quiz_performance_chart, create_boxplot_chart,
                     create_section_comparison_chart, create_percentiles_chart,
                     create_outliers_chart, create_most_improved_chart)
from reports import ReportGenerator  # Generate text summary reports

# Page config - set up the Streamlit page with title and wide layout
st.set_page_config(page_title="Academic Analytics Lite", layout="wide")

# Initialize session state - load config first, then students
# Session state keeps data persistent across page refreshes
if 'config' not in st.session_state:
    st.session_state.config = load_config()  # Load configuration from config.json
if 'students' not in st.session_state:
    st.session_state.students = transform_students(
        read_csv())  # Load and transform student data


# Convert student dict to be more user-friendly for the table display
def student_to_dict_row(s):
    return {
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
    }


# Convert student list to DataFrame for tables
def students_to_dataframe(students):
    if not students:
        return pd.DataFrame()
    return pd.DataFrame([student_to_dict_row(s) for s in students])


def render_config_display():  # Display config settings in sidebar
    st.header("Config")
    weights = st.session_state.config['weights']  # Get config values
    grade_scale = st.session_state.config['grade_scale']
    at_risk_threshold = st.session_state.config.get(
        'thresholds', {}).get('at_risk', 60)
    st.caption(
        f"**Weights:** Quiz {weights['quizzes']*100:.0f}% | Mid {weights['midterm']*100:.0f}% | Final {weights['final']*100:.0f}% | Attendance {weights['attendance']*100:.0f}%")
    st.caption(
        f"**Grade Scale:** A: {grade_scale['A']}+ | B: {grade_scale['B']}+ | C: {grade_scale['C']}+ | D: {grade_scale['D']}+")
    st.caption(f"**At-Risk:** Below {at_risk_threshold} (Grade F)")


# Save CSV and create download button
def save_and_download_csv(students, filename, label, key, output_dir):
    csv_data = students_to_dataframe(students).to_csv(
        index=False)  # Convert to CSV
    with open(os.path.join(output_dir, filename), 'w') as f:  # Save to file
        f.write(csv_data)
    st.download_button(label=label, data=csv_data, file_name=filename,
                       mime="text/csv", key=key, use_container_width=True)  # Download button


# Render export section with download buttons
def render_export_section(output_dir):
    st.subheader("Export Data")
    at_risk_students = get_at_risk_students(
        st.session_state.students, 60.0)  # Get at-risk students
    if at_risk_students:  # Create download button if any exist
        save_and_download_csv(at_risk_students, 'at_risk_students.csv',
                              "At-Risk Students CSV", "download_at_risk", output_dir)
    sections = sorted(set(s.get('section') for s in st.session_state.students if s.get(
        'section')))  # Get all sections
    for section in sections:  # Create download button for each section
        section_students = [
            s for s in st.session_state.students if s.get('section') == section]
        save_and_download_csv(
            section_students, f'section_{section}.csv', f"Section {section} CSV", f"download_section_{section}", output_dir)


# Sidebar with config and export
with st.sidebar:
    render_config_display()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir_sidebar = os.path.normpath(
        os.path.join(script_dir, '..', 'data', 'output'))
    os.makedirs(output_dir_sidebar, exist_ok=True)
    render_export_section(output_dir_sidebar)

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


def render_student_form_fields():  # Render form fields in 3 columns
    col1, col2, col3 = st.columns(3)  # Create 3 columns
    with col1:  # Student info
        student_id = st.text_input("Student ID")
        last_name = st.text_input("Last Name")
        first_name = st.text_input("First Name")
        section = st.text_input("Section")
    with col2:  # Quiz scores
        quiz1 = st.number_input("Quiz 1", 0.0, 100.0, 0.0)
        quiz2 = st.number_input("Quiz 2", 0.0, 100.0, 0.0)
        quiz3 = st.number_input("Quiz 3", 0.0, 100.0, 0.0)
        quiz4 = st.number_input("Quiz 4", 0.0, 100.0, 0.0)
        quiz5 = st.number_input("Quiz 5", 0.0, 100.0, 0.0)
    with col3:  # Exams and attendance
        midterm = st.number_input("Midterm", 0.0, 100.0, 0.0)
        final = st.number_input("Final", 0.0, 100.0, 0.0)
        attendance = st.number_input("Attendance %", 0.0, 100.0, 0.0)
    return student_id, last_name, first_name, section, quiz1, quiz2, quiz3, quiz4, quiz5, midterm, final, attendance


def render_add_student_form():  # Render form for adding new student
    with st.expander("Add New Student"):  # Collapsible section
        with st.form("add_student_form"):  # Form with submit button
            student_id, last_name, first_name, section, quiz1, quiz2, quiz3, quiz4, quiz5, midterm, final, attendance = render_student_form_fields()
            submitted = st.form_submit_button("Add Student")
            if submitted:  # On submit
                new_student = {'student_id': student_id, 'last_name': last_name, 'first_name': first_name,
                               'section': section, 'quiz1': quiz1, 'quiz2': quiz2, 'quiz3': quiz3,
                               'quiz4': quiz4, 'quiz5': quiz5, 'midterm': midterm, 'final': final,
                               'attendance_percent': attendance}
                st.session_state.students = insert_student(
                    st.session_state.students, new_student)  # Add student
                st.success(f"Added {first_name} {last_name}!")
                st.rerun()  # Refresh page


# Add new student (collapsible)
render_add_student_form()


def render_delete_student_form():  # Render form for deleting student
    with st.expander("Delete Student"):  # Collapsible section
        student_names = [
            # Student list
            f"{s.get('student_id', '')} - {s.get('first_name', '')} {s.get('last_name', '')}" for s in st.session_state.students]
        col1, col2 = st.columns([3, 1])  # 2 columns for dropdown and button
        with col1:  # Dropdown
            selected_student = st.selectbox(
                "Select student", student_names, label_visibility="collapsed")
        with col2:  # Delete button
            if st.button("Delete", type="primary"):
                selected_id = selected_student.split(' - ')[0]  # Extract ID
                st.session_state.students = delete_student(
                    st.session_state.students, selected_id)  # Remove student
                st.success(f"Deleted {selected_id}!")
                st.rerun()  # Refresh page


# Delete student
render_delete_student_form()

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


def render_chart(title, chart_func, filename, output_dir):  # Display chart and save to file
    st.subheader(title)
    fig = chart_func(st.session_state.students)  # Generate chart
    if fig:
        st.pyplot(fig)  # Display in Streamlit
        fig.savefig(os.path.join(output_dir, filename),
                    dpi=150, bbox_inches='tight')  # Save as PNG


def basic_charts(output_dir):  # Render 3 basic charts side by side
    col1, col2, col3 = st.columns(3)  # 3 columns
    with col1:  # Grade distribution
        render_chart("Grade Distribution", create_grade_distribution_chart,
                     'grade_distribution.png', output_dir)
    with col2:  # Letter grades
        render_chart("Letter Grades", create_letter_grades_chart,
                     'letter_grades.png', output_dir)
    with col3:  # Quiz performance
        render_chart("Quiz Performance", create_quiz_performance_chart,
                     'quiz_performance.png', output_dir)


def advanced_charts(output_dir):  # Render 3 advanced charts side by side
    col1, col2, col3 = st.columns(3)  # 3 columns
    with col1:  # Percentiles
        render_chart("Grade Percentiles", create_percentiles_chart,
                     'grade_percentiles.png', output_dir)
    with col2:  # Outliers
        render_chart("Outlier Detection", create_outliers_chart,
                     'outlier_detection.png', output_dir)
    with col3:  # Most improved
        render_chart("Students Improvement", create_most_improved_chart,
                     'most_improved.png', output_dir)


basic_charts(output_dir)
advanced_charts(output_dir)

# Section Comparison gets its own full-width row
render_chart("Section Comparison", create_section_comparison_chart,
             'section_comparison.png', output_dir)

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


# Build row for section comparison table
def build_section_data_row(section, data):
    stats = data['statistics']
    letter_dist = data['letter_grades']
    return {
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
    }


# Render 2 tables comparing sections
def render_section_comparison_tables(analytics):
    st.subheader("Section Comparison")
    section_stats = analytics.get_section_comparison()  # Get section stats
    if section_stats and len(section_stats) > 0:
        section_data = [build_section_data_row(
            # Build rows
            section, data) for section, data in sorted(section_stats.items())]
        section_df = pd.DataFrame(section_data)  # Convert to DataFrame
        col1, col2 = st.columns([2, 1])  # 2 columns (2:1 ratio)
        with col1:  # Performance metrics
            st.write("**Performance Metrics**")
            st.dataframe(section_df[['Section', 'Students', 'Mean', 'Median',
                         'Std Dev', 'Min', 'Max']], width='stretch', hide_index=True)
        with col2:  # Grade distribution
            st.write("**Grade Distribution**")
            st.dataframe(
                section_df[['Section', 'A', 'B', 'C', 'D', 'F']], width='stretch', hide_index=True)
    else:
        st.info("No section data available")


# Section Comparison Tables
render_section_comparison_tables(analytics)

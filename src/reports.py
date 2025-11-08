import os
from typing import List, Dict, Any
import pandas as pd
import numpy as np


# Generate text summary report
def generate_summary_report(students: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
    total = len(students)  # Count total students
    with_grades = [s for s in students if s.get('final_grade') is not None and not pd.isna(
        s.get('final_grade'))]  # Filter complete data

    if not with_grades:
        return "No students with complete grade data available."

    df = pd.DataFrame(with_grades)  # Convert to DataFrame
    grades = df['final_grade'].values  # Extract grades

    avg_grade = np.mean(grades)  # Calculate statistics
    median_grade = np.median(grades)
    min_grade = np.min(grades)
    max_grade = np.max(grades)

    letter_counts = {'A': 0, 'B': 0, 'C': 0,
                     'D': 0, 'F': 0}  # Count letter grades
    for student in with_grades:
        grade = student.get('letter_grade')
        if grade in letter_counts:
            letter_counts[grade] += 1

    at_risk_threshold = config.get('thresholds', {}).get(
        'at_risk', 60)  # Get threshold from config

    at_risk = df[df['final_grade'] < at_risk_threshold].to_dict(
        'records')  # Filter at-risk students
    top_performers = df[df['letter_grade'] == 'A'].to_dict(
        'records')  # Filter A students

    section_stats = df.groupby('section').agg({  # Group by section
        'final_grade': list,
        'letter_grade': lambda x: (x == 'A').sum()
    }).to_dict()

    sections = section_stats.get('final_grade', {})
    section_a_grades = section_stats.get('letter_grade', {})

    passing = (df['letter_grade'].isin(['A', 'B', 'C'])
               ).sum()  # Calculate pass rate
    pass_rate = (passing / len(df) * 100) if len(df) > 0 else 0

    lines = []  # Build report text
    lines.append("OVERVIEW:")
    lines.append(f"  Total Students: {total}")
    lines.append(f"  Students with Complete Data: {len(with_grades)}")
    lines.append(f"  Students with Missing Data: {total - len(with_grades)}")
    lines.append("")

    lines.append("GRADE STATISTICS:")
    lines.append(f"  Average Final Grade: {avg_grade:.2f}")
    lines.append(f"  Median Final Grade: {median_grade:.2f}")
    lines.append(f"  Highest Grade: {max_grade:.2f}")
    lines.append(f"  Lowest Grade: {min_grade:.2f}")
    lines.append(f"  Pass Rate (C or better): {pass_rate:.1f}%")
    lines.append("")

    lines.append("STUDENTS WITH GRADE A BY SECTION:")
    if section_a_grades:
        for section in sorted(section_a_grades.keys()):
            a_count = section_a_grades[section]
            lines.append(f"  Section {section}: {a_count} students")
    else:
        lines.append("  No sections found")
    lines.append("")

    lines.append("PERFORMANCE CATEGORIES:")
    lines.append(f" Top Performers (Grade A): {len(top_performers)} students")
    lines.append(
        f"  At-Risk (Below {at_risk_threshold}): {len(at_risk)} students")
    lines.append("")

    if sections:  # Add section breakdown
        lines.append("SECTION BREAKDOWN:")
        for section in sorted(sections.keys()):
            section_grades = sections[section]
            section_avg = sum(section_grades) / len(section_grades)
            lines.append(
                f"  Section {section}: {len(section_grades)} students, Avg: {section_avg:.2f}")
        lines.append("")

    if at_risk:  # Add at-risk student details
        lines.append(f"AT-RISK STUDENTS (Below {at_risk_threshold}):")
        lines.append(f"  Total: {len(at_risk)} students")
        for student in sorted(at_risk, key=lambda x: x['final_grade'])[:10]:
            lines.append(f"    - {student['first_name']} {student['last_name']} "
                         f"(ID: {student['student_id']}): {student['final_grade']:.2f}")
        if len(at_risk) > 10:
            lines.append(f"    ... and {len(at_risk) - 10} more")
        lines.append("")

    return "\n".join(lines)


class ReportGenerator:  # Wrapper class for report generation
    # Initialize with student data and config
    def __init__(self, students: List[Dict[str, Any]], config: Dict[str, Any]):
        self.students = students
        self.config = config

    def generate_summary_report(self) -> str:  # Generate summary report
        return generate_summary_report(self.students, self.config)

import json
import os
from typing import List, Dict, Any
from datetime import datetime


class ReportGenerator:
    # Generates various text-based reports for student data analysis

    def __init__(self, students: List[Dict[str, Any]], config: Dict[str, Any]):
        self.students = students
        self.config = config
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_summary_report(self) -> str:
        # Generate overall summary report
        total_students = len(self.students)
        students_with_grades = [
            s for s in self.students if s.get('final_grade') is not None]

        # Calculate overall statistics
        final_grades = [s['final_grade'] for s in students_with_grades]
        avg_grade = sum(final_grades) / \
            len(final_grades) if final_grades else 0

        # Letter grade distribution
        letter_counts = {}
        for grade in ['A', 'B', 'C', 'D', 'F']:
            letter_counts[grade] = sum(
                1 for s in students_with_grades if s.get('letter_grade') == grade)

        # At-risk students
        at_risk_threshold = self.config.get(
            'thresholds', {}).get('at_risk', 60)
        at_risk = [
            s for s in students_with_grades if s['final_grade'] < at_risk_threshold]

        report = []
        report.append("STUDENT PERFORMANCE SUMMARY REPORT")
        report.append(f"Generated: {self.timestamp}")
        report.append("")

        report.append("OVERVIEW:")
        report.append(f"  Total Students: {total_students}")
        report.append(
            f"  Students with Complete Data: {len(students_with_grades)}")
        report.append(
            f"  Students with Missing Data: {total_students - len(students_with_grades)}")
        report.append(f"  Average Final Grade: {avg_grade:.2f}")
        report.append("")

        report.append("LETTER GRADE DISTRIBUTION:")
        for grade, count in letter_counts.items():
            percentage = (count / len(students_with_grades) *
                          100) if students_with_grades else 0
            report.append(f"  {grade}: {count} students ({percentage:.1f}%)")
        report.append("")

        report.append(f"AT-RISK STUDENTS (Below {at_risk_threshold}):")
        report.append(f"  Total: {len(at_risk)} students")
        if at_risk:
            for student in at_risk[:10]:  # Show first 10
                report.append(f"    - {student['first_name']} {student['last_name']} "
                              f"(ID: {student['student_id']}): {student['final_grade']:.2f}")
            if len(at_risk) > 10:
                report.append(f"    ... and {len(at_risk) - 10} more")
        report.append("")

        report.append("=" * 80)
        return "\n".join(report)

    def generate_student_report(self, student: Dict[str, Any]) -> str:
        # Generate individual student report
        report = []
        report.append("=" * 80)
        report.append("INDIVIDUAL STUDENT REPORT")
        report.append("=" * 80)
        report.append(f"Student ID: {student.get('student_id', 'N/A')}")
        report.append(
            f"Name: {student.get('first_name', '')} {student.get('last_name', '')}")
        report.append(f"Section: {student.get('section', 'N/A')}")
        report.append("")

        report.append("QUIZ SCORES:")
        quizzes = []
        for i in range(1, 6):
            score = student.get(f'quiz{i}')
            if score is not None:
                report.append(f"  Quiz {i}: {score:.2f}")
                quizzes.append(score)
            else:
                report.append(f"  Quiz {i}: Missing")

        quiz_avg = student.get('quiz_avg')
        if quiz_avg is not None:
            report.append(f"  Quiz Average: {quiz_avg:.2f}")
        report.append("")

        report.append("EXAM SCORES:")
        midterm = student.get('midterm')
        final = student.get('final')
        report.append(
            f"  Midterm: {midterm:.2f}" if midterm is not None else "  Midterm: Missing")
        report.append(
            f"  Final: {final:.2f}" if final is not None else "  Final: Missing")
        report.append("")

        report.append("ATTENDANCE:")
        attendance = student.get('attendance')
        report.append(
            f"  Attendance: {attendance:.2f}" if attendance is not None else "  Attendance: Missing")
        report.append("")

        report.append("FINAL GRADE:")
        final_grade = student.get('final_grade')
        letter = student.get('letter_grade')
        if final_grade is not None:
            report.append(f"  Numeric: {final_grade:.2f}")
            report.append(f"  Letter: {letter}")
        else:
            report.append("  Grade cannot be calculated (missing data)")
        report.append("")

        report.append("=" * 80)
        return "\n".join(report)

    def generate_section_report(self, section: str) -> str:
        # Generate report for a specific section
        section_students = [
            s for s in self.students if s.get('section') == section]
        students_with_grades = [
            s for s in section_students if s.get('final_grade') is not None]
        students_missing_grades = [
            s for s in section_students if s.get('final_grade') is None]

        if not section_students:
            return f"No students found in section {section}"

        final_grades = [s['final_grade'] for s in students_with_grades]
        avg_grade = sum(final_grades) / \
            len(final_grades) if final_grades else 0

        # Letter grade distribution
        letter_counts = {}
        for grade in ['A', 'B', 'C', 'D', 'F']:
            letter_counts[grade] = sum(
                1 for s in students_with_grades if s.get('letter_grade') == grade)

        report = []
        report.append("=" * 80)
        report.append(f"SECTION {section} REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {self.timestamp}")
        report.append("")

        report.append("SECTION OVERVIEW:")
        report.append(f"  Total Students: {len(section_students)}")
        report.append(
            f"  Students with Complete Data: {len(students_with_grades)}")
        report.append(
            f"  Students with Missing Data: {len(students_missing_grades)}")
        report.append(f"  Average Grade: {avg_grade:.2f}")
        report.append("")

        report.append("LETTER GRADE DISTRIBUTION:")
        total = len(students_with_grades)
        for grade, count in letter_counts.items():
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {grade}: {count} students ({percentage:.1f}%)")
        report.append("")

        report.append("STUDENT LIST:")
        # Sort by final grade descending
        sorted_students = sorted(students_with_grades,
                                 key=lambda x: x['final_grade'], reverse=True)
        for i, student in enumerate(sorted_students, 1):
            report.append(f"  {i}. {student['first_name']} {student['last_name']} - "
                          f"{student['final_grade']:.2f} ({student['letter_grade']})")
        report.append("")

        report.append("=" * 80)
        return "\n".join(report)

    def generate_at_risk_report(self) -> str:
        # Generate detailed report for at-risk students
        at_risk_threshold = self.config.get(
            'thresholds', {}).get('at_risk', 60)
        students_with_grades = [
            s for s in self.students if s.get('final_grade') is not None]
        at_risk = [
            s for s in students_with_grades if s['final_grade'] < at_risk_threshold]

        # Sort by grade (lowest first)
        at_risk.sort(key=lambda x: x['final_grade'])

        report = []
        report.append("=" * 80)
        report.append("AT-RISK STUDENTS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {self.timestamp}")
        report.append(f"Threshold: Below {at_risk_threshold}")
        report.append("")

        report.append(f"TOTAL AT-RISK STUDENTS: {len(at_risk)}")
        report.append("")

        if at_risk:
            report.append("DETAILED LIST:")
            for i, student in enumerate(at_risk, 1):
                report.append(
                    f"\n{i}. {student['first_name']} {student['last_name']}")
                report.append(f"   Student ID: {student['student_id']}")
                report.append(f"   Section: {student['section']}")
                report.append(
                    f"   Final Grade: {student['final_grade']:.2f} ({student['letter_grade']})")

                # Show weak areas
                report.append("   Component Breakdown:")
                if student.get('quiz_avg') is not None:
                    report.append(
                        f"     Quiz Average: {student['quiz_avg']:.2f}")
                if student.get('midterm') is not None:
                    report.append(f"     Midterm: {student['midterm']:.2f}")
                if student.get('final') is not None:
                    report.append(f"     Final Exam: {student['final']:.2f}")
                if student.get('attendance') is not None:
                    report.append(
                        f"     Attendance: {student['attendance']:.2f}")
        else:
            report.append("No students are currently at risk!")

        report.append("")
        report.append("=" * 80)
        return "\n".join(report)

    def generate_top_performers_report(self, top_n: int = 10) -> str:
        # Generate report for top performing students
        students_with_grades = [
            s for s in self.students if s.get('final_grade') is not None]
        top_students = sorted(
            students_with_grades, key=lambda x: x['final_grade'], reverse=True)[:top_n]

        report = []
        report.append("=" * 80)
        report.append(f"TOP {top_n} PERFORMERS")
        report.append("=" * 80)
        report.append(f"Generated: {self.timestamp}")
        report.append("")

        for i, student in enumerate(top_students, 1):
            report.append(
                f"{i}. {student['first_name']} {student['last_name']}")
            report.append(f"   Student ID: {student['student_id']}")
            report.append(f"   Section: {student['section']}")
            report.append(
                f"   Final Grade: {student['final_grade']:.2f} ({student['letter_grade']})")
            report.append("")

        report.append("=" * 80)
        return "\n".join(report)

    def export_to_json(self, output_path: str):
        # Export processed student data to JSON
        data = {
            'metadata': {
                'generated': self.timestamp,
                'total_students': len(self.students),
                'config': self.config
            },
            'students': self.students
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def export_section_csv(self, section: str, output_path: str):
        # Export section data to CSV file
        import csv

        section_students = [
            s for s in self.students if s.get('section') == section]

        if not section_students:
            return

        # Define CSV columns
        fieldnames = ['student_id', 'last_name', 'first_name', 'section',
                      'quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5',
                      'quiz_avg', 'midterm', 'final', 'attendance',
                      'final_grade', 'letter_grade']

        # Numeric fields to round to 2 decimal places
        numeric_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5',
                          'quiz_avg', 'midterm', 'final', 'attendance', 'final_grade']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for student in section_students:
                row = {}
                for field in fieldnames:
                    value = student.get(field, '')
                    # Round numeric fields to 2 decimal places
                    if field in numeric_fields and value != '' and value is not None:
                        value = round(value, 2)
                    row[field] = value
                writer.writerow(row)

    def export_at_risk_csv(self, output_path: str):
        # Export at-risk students to CSV file
        import csv

        at_risk_threshold = self.config.get(
            'thresholds', {}).get('at_risk', 60)
        students_with_grades = [
            s for s in self.students if s.get('final_grade') is not None]
        at_risk = [
            s for s in students_with_grades if s['final_grade'] < at_risk_threshold]

        if not at_risk:
            return

        # Define CSV columns
        fieldnames = ['student_id', 'last_name', 'first_name', 'section',
                      'quiz_avg', 'midterm', 'final', 'attendance',
                      'final_grade', 'letter_grade']

        # Numeric fields to round to 2 decimal places
        numeric_fields = ['quiz_avg', 'midterm',
                          'final', 'attendance', 'final_grade']

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for student in sorted(at_risk, key=lambda x: x['final_grade']):
                row = {}
                for field in fieldnames:
                    value = student.get(field, '')
                    # Round numeric fields to 2 decimal places
                    if field in numeric_fields and value != '' and value is not None:
                        value = round(value, 2)
                    row[field] = value
                writer.writerow(row)

    def save_all_reports(self, output_folder: str):
        # Export CSV files and print summary to console
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Print summary to console
        print(self.generate_summary_report())
        print()

        # Export at-risk CSV
        self.export_at_risk_csv(os.path.join(
            output_folder, 'at_risk_students.csv'))

        # Export per-section CSVs
        sections = set(s.get('section')
                       for s in self.students if s.get('section'))
        for section in sections:
            self.export_section_csv(section, os.path.join(
                output_folder, f'section_{section}.csv'))

        print(f"CSV reports exported to: {output_folder}")

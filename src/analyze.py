import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
from collections import Counter


# Get final grade statistics for all students
def get_final_grade_stats(students: List[Dict[str, Any]]) -> Dict[str, float]:
    grades = [s['final_grade']
              for s in students if s.get('final_grade') is not None]
    if not grades:
        return {}

    grades_array = np.array(grades)
    return {
        'mean': np.mean(grades_array),
        'median': np.median(grades_array),
        'mode': float(Counter(grades).most_common(1)[0][0]) if grades else 0,
        'std_dev': np.std(grades_array),
        'min': np.min(grades_array),
        'max': np.max(grades_array),
        'range': np.max(grades_array) - np.min(grades_array)
    }


# Get percentiles for final grades
def get_grade_percentiles(students: List[Dict[str, Any]]) -> Dict[str, float]:
    grades = [s['final_grade']
              for s in students if s.get('final_grade') is not None]
    if not grades:
        return {}

    grades_array = np.array(grades)
    return {
        'p25': np.percentile(grades_array, 25),
        'p50': np.percentile(grades_array, 50),
        'p75': np.percentile(grades_array, 75),
        'p90': np.percentile(grades_array, 90),
        'p95': np.percentile(grades_array, 95)
    }


# Detect outliers using IQR (Interquartile Range) method
def detect_outliers_iqr(data: List[float]) -> Dict[str, Any]:
    if not data or len(data) < 4:
        return {'lower_outliers': [], 'upper_outliers': [], 'method': 'IQR'}

    grades_array = np.array(data)
    q1 = np.percentile(grades_array, 25)
    q3 = np.percentile(grades_array, 75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    lower_outliers = [x for x in data if x < lower_bound]
    upper_outliers = [x for x in data if x > upper_bound]

    return {
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'lower_outliers': lower_outliers,
        'upper_outliers': upper_outliers,
        'method': 'IQR'
    }


# Compare statistics across sections using array operations
def get_section_comparison(students: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    sections = {}

    # Group grades by section using array operations
    for student in students:
        section = student.get('section')
        grade = student.get('final_grade')

        if section and grade is not None:
            if section not in sections:
                sections[section] = []
            sections[section].append(grade)

    # Calculate stats for each section using numpy
    section_stats = {}
    for section, grades in sections.items():
        grades_array = np.array(grades)
        letter_grades = [s['letter_grade'] for s in students
                         if s.get('section') == section and s.get('letter_grade')]

        section_stats[section] = {
            'statistics': {
                'mean': np.mean(grades_array),
                'median': np.median(grades_array),
                'mode': float(Counter(grades).most_common(1)[0][0]) if grades else 0,
                'std_dev': np.std(grades_array),
                'min': np.min(grades_array),
                'max': np.max(grades_array),
                'range': np.max(grades_array) - np.min(grades_array)
            },
            'count': len(grades_array),
            'letter_grades': dict(Counter(letter_grades))
        }

    return section_stats


# VISUALIZATION FUNCTIONS (return fig objects for Streamlit)
def create_grade_distribution_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    grades = np.array([s['final_grade']
                      for s in students if s.get('final_grade') is not None])
    if len(grades) == 0:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(grades, bins=15, alpha=0.7, color='#2E86AB', edgecolor='black')
    ax.set_xlabel('Grade', fontsize=7)
    ax.set_ylabel('Students', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def create_letter_grades_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    letter_grades = [s['letter_grade']
                     for s in students if s.get('letter_grade')]
    if not letter_grades:
        return None
    grade_counts = Counter(letter_grades)
    grades = ['A', 'B', 'C', 'D', 'F']
    counts = [grade_counts.get(g, 0) for g in grades]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(grades, counts, color=colors, alpha=0.7, edgecolor='black')
    ax.set_xlabel('Grade', fontsize=7)
    ax.set_ylabel('Students', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def create_quiz_performance_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    # Calculate quiz stats inline
    quiz_means = []
    quiz_labels = []
    for i in range(1, 6):
        quiz_key = f'quiz{i}'
        scores = [s[quiz_key] for s in students if s.get(quiz_key) is not None]
        if scores:
            quiz_means.append(np.mean(scores))
            quiz_labels.append(quiz_key)

    if not quiz_means:
        return None

    means = np.array(quiz_means)
    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(range(len(quiz_labels)), means, alpha=0.7,
           color='#2E86AB', edgecolor='black')
    ax.set_xlabel('Quiz', fontsize=7)
    ax.set_ylabel('Avg', fontsize=7)
    ax.set_xticks(range(len(quiz_labels)))
    ax.set_xticklabels([q.upper() for q in quiz_labels], fontsize=6)
    ax.set_ylim(0, 100)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def create_boxplot_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    grades = np.array([s['final_grade']
                      for s in students if s.get('final_grade') is not None])
    if len(grades) == 0:
        return None
    fig, ax = plt.subplots(figsize=figsize)
    box_plot = ax.boxplot(grades, vert=True, patch_artist=True)
    box_plot['boxes'][0].set_facecolor('#2E86AB')
    ax.set_ylabel('Grade', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


def create_percentiles_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    # Create a bar chart showing grade percentiles (25th, 50th, 75th, 90th, 95th)
    percentiles = get_grade_percentiles(students)
    if not percentiles:
        return None

    labels = ['25th', '50th', '75th', '90th', '95th']
    values = [percentiles['p25'], percentiles['p50'], percentiles['p75'],
              percentiles['p90'], percentiles['p95']]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(labels, values, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=1)
    ax.set_ylabel('Grade', fontsize=8)
    ax.set_xlabel('Percentile', fontsize=8)
    ax.set_ylim(0, 100)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=7)

    plt.tight_layout()
    return fig


def create_outliers_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    # Create a box plot chart to show outliers using the IQR (Interquartile Range) method
    grades = np.array([s['final_grade']
                      for s in students if s.get('final_grade') is not None])
    if len(grades) == 0:
        return None

    outlier_info = detect_outliers_iqr(grades.tolist())

    fig, ax = plt.subplots(figsize=figsize)

    # Create box plot
    box_plot = ax.boxplot(grades, vert=True, patch_artist=True, widths=0.5)
    box_plot['boxes'][0].set_facecolor('#2E86AB')
    box_plot['boxes'][0].set_alpha(0.7)

    # Highlight outliers
    lower_bound = outlier_info['lower_bound']
    upper_bound = outlier_info['upper_bound']

    # Add horizontal lines for bounds
    ax.axhline(y=lower_bound, color='red', linestyle='--', linewidth=1.5,
               label=f'Lower Bound: {lower_bound:.1f}')
    ax.axhline(y=upper_bound, color='red', linestyle='--', linewidth=1.5,
               label=f'Upper Bound: {upper_bound:.1f}')

    ax.set_ylabel('Grade', fontsize=8)
    ax.set_title('Outlier Detection (IQR Method)',
                 fontsize=9, fontweight='bold')
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_xticks([])

    plt.tight_layout()
    return fig


def create_most_improved_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    # Create a bar chart showing top 10 most improved students (midterm to final exam)
    improvements = []

    for student in students:
        midterm = student.get('midterm')
        final_exam = student.get('final')

        if midterm is not None and final_exam is not None:
            improvement = final_exam - midterm
            improvements.append({
                'student_id': student.get('student_id'),
                'first_name': student.get('first_name'),
                'last_name': student.get('last_name'),
                'midterm': midterm,
                'final_exam': final_exam,
                'improvement': improvement
            })

    if not improvements:
        return None

    # Sort by improvement and get top 10
    most_improved = sorted(
        improvements, key=lambda x: x['improvement'], reverse=True)[:10]

    names = [f"{s['first_name'][0]}. {s['last_name']}" for s in most_improved]
    midterms = [s['midterm'] for s in most_improved]
    final_exams = [s['final_exam'] for s in most_improved]
    improvements_vals = [s['improvement'] for s in most_improved]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=figsize)
    bars1 = ax.bar(x - width/2, midterms, width, label='Midterm',
                   color='#A23B72', alpha=0.8, edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x + width/2, final_exams, width, label='Final Exam',
                   color='#6A994E', alpha=0.8, edgecolor='black', linewidth=0.8)

    ax.set_ylabel('Grade', fontsize=8)
    ax.set_xlabel('Students', fontsize=8)
    ax.set_title('Top 10 Most Improved Students',
                 fontsize=9, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=6)
    ax.set_ylim(0, 100)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3, axis='y')

    # Add improvement values on top
    for i, imp in enumerate(improvements_vals):
        ax.text(i, max(midterms[i], final_exams[i]) + 2, f'+{imp:.1f}',
                ha='center', va='bottom', fontsize=6, color='green', fontweight='bold')

    plt.tight_layout()
    return fig


def create_section_comparison_chart(students: List[Dict[str, Any]], figsize=(6, 3)):
    # Create a 4-panel chart comparing different sections (mean scores, grade distribution, min/max range, pass rate)
    section_stats = get_section_comparison(students)
    if not section_stats or len(section_stats) < 1:
        return None

    sections = sorted(section_stats.keys())

    # Extract metrics for each section
    means = np.array([section_stats[s]['statistics']['mean']
                     for s in sections])
    mins = np.array([section_stats[s]['statistics']['min'] for s in sections])
    maxs = np.array([section_stats[s]['statistics']['max'] for s in sections])

    # Calculate pass rate (A, B, C grades)
    pass_rates = []
    for section in sections:
        letter_grades = section_stats[section]['letter_grades']
        total = section_stats[section]['count']
        passing = letter_grades.get(
            'A', 0) + letter_grades.get('B', 0) + letter_grades.get('C', 0)
        pass_rate = (passing / total * 100) if total > 0 else 0
        pass_rates.append(pass_rate)
    pass_rates = np.array(pass_rates)

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Section Performance Comparison',
                 fontsize=9, fontweight='bold')

    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4749']

    # Plot 1: Mean scores
    ax1 = axes[0, 0]
    bars1 = ax1.bar(sections, means, alpha=0.8, color=colors[:len(
        sections)], edgecolor='black', linewidth=0.8)
    ax1.set_ylabel('Mean Grade', fontsize=7)
    ax1.set_ylim(0, 100)
    ax1.tick_params(labelsize=6)
    ax1.grid(True, alpha=0.3, axis='y')
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}',
                 ha='center', va='bottom', fontsize=6)

    # Plot 2: Letter grade distribution (grouped bars)
    ax2 = axes[0, 1]
    grades = ['A', 'B', 'C', 'D', 'F']
    grade_colors = {'A': '#2E86AB', 'B': '#A23B72',
                    'C': '#F18F01', 'D': '#C73E1D', 'F': '#3B1F2B'}
    x_pos = np.arange(len(sections))
    width = 0.15

    for i, grade in enumerate(grades):
        counts = [section_stats[s]['letter_grades'].get(
            grade, 0) for s in sections]
        offset = (i - 2) * width
        ax2.bar(x_pos + offset, counts, width, label=grade, alpha=0.8,
                color=grade_colors[grade], edgecolor='black', linewidth=0.8)

    ax2.set_ylabel('Student Count', fontsize=7)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(sections)
    ax2.tick_params(labelsize=6)
    ax2.legend(fontsize=6, loc='upper right', ncol=5)
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Min/Max range
    ax3 = axes[1, 0]
    x_pos = np.arange(len(sections))
    width = 0.35
    bars3a = ax3.bar(x_pos - width/2, mins, width, label='Min', alpha=0.8,
                     color='#C73E1D', edgecolor='black', linewidth=0.8)
    bars3b = ax3.bar(x_pos + width/2, maxs, width, label='Max', alpha=0.8,
                     color='#6A994E', edgecolor='black', linewidth=0.8)
    ax3.set_ylabel('Grade Range', fontsize=7)
    ax3.set_xlabel('Section', fontsize=7)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(sections)
    ax3.set_ylim(0, 100)
    ax3.tick_params(labelsize=6)
    ax3.legend(fontsize=6, loc='upper left')
    ax3.grid(True, alpha=0.3, axis='y')

    # Plot 4: Pass rate
    ax4 = axes[1, 1]
    bars4 = ax4.bar(sections, pass_rates, alpha=0.8, color=colors[:len(
        sections)], edgecolor='black', linewidth=0.8)
    ax4.set_ylabel('Pass Rate (%)', fontsize=7)
    ax4.set_xlabel('Section', fontsize=7)
    ax4.set_ylim(0, 100)
    ax4.tick_params(labelsize=6)
    ax4.grid(True, alpha=0.3, axis='y')
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}%',
                 ha='center', va='bottom', fontsize=6)

    plt.tight_layout()
    return fig


class StudentAnalytics:
    def __init__(self, students: List[Dict[str, Any]]):
        self.students = students

    def get_final_grade_statistics(self):
        return get_final_grade_stats(self.students)

    def get_section_comparison(self):
        return get_section_comparison(self.students)

    def get_percentiles(self):
        return get_grade_percentiles(self.students)

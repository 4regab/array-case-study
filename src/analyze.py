import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any
from collections import Counter


# Calculate basic statistics for final grades
def get_final_grade_stats(students: List[Dict[str, Any]]) -> Dict[str, float]:
    grades = [s['final_grade'] for s in students if s.get(
        'final_grade') is not None]  # Extract all grades
    if not grades:
        return {}
    grades_array = np.array(grades)  # Convert to numpy array
    return {
        'mean': np.mean(grades_array),  # Average
        'median': np.median(grades_array),  # Middle value
        # Most common
        'mode': float(Counter(grades).most_common(1)[0][0]) if grades else 0,
        'std_dev': np.std(grades_array),  # Spread
        'min': np.min(grades_array),  # Lowest
        'max': np.max(grades_array),  # Highest
        'range': np.max(grades_array) - np.min(grades_array)  # Range
    }


# Calculate grade percentiles (25th, 50th, 75th, 90th, 95th)
def get_grade_percentiles(students: List[Dict[str, Any]]) -> Dict[str, float]:
    grades = [s['final_grade'] for s in students if s.get(
        'final_grade') is not None]  # Extract grades
    if not grades:
        return {}
    grades_array = np.array(grades)  # Convert to numpy array
    return {
        'p25': np.percentile(grades_array, 25),  # 25% scored below this
        # 50% scored below this (median)
        'p50': np.percentile(grades_array, 50),
        'p75': np.percentile(grades_array, 75),  # 75% scored below this
        'p90': np.percentile(grades_array, 90),  # 90% scored below this
        'p95': np.percentile(grades_array, 95)   # 95% scored below this
    }


# Find outliers using IQR method (1.5 * IQR from Q1/Q3)
def detect_outliers_iqr(data: List[float]) -> Dict[str, Any]:
    if not data or len(data) < 4:  # Need at least 4 data points
        return {'lower_outliers': [], 'upper_outliers': [], 'method': 'IQR'}

    grades_array = np.array(data)  # Convert to numpy array
    q1 = np.percentile(grades_array, 25)  # 25th percentile
    q3 = np.percentile(grades_array, 75)  # 75th percentile
    iqr = q3 - q1  # Interquartile range

    lower_bound = q1 - 1.5 * iqr  # Lower outlier threshold
    upper_bound = q3 + 1.5 * iqr  # Upper outlier threshold

    lower_outliers = [x for x in data if x <
                      lower_bound]  # Unusually low grades
    upper_outliers = [x for x in data if x >
                      upper_bound]  # Unusually high grades

    return {
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'lower_outliers': lower_outliers,
        'upper_outliers': upper_outliers,
        'method': 'IQR'
    }


# Compare statistics across sections
def get_section_comparison(students: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    sections = {}

    for student in students:  # Group grades by section
        section = student.get('section')
        grade = student.get('final_grade')
        if section and grade is not None:
            if section not in sections:
                sections[section] = []
            sections[section].append(grade)

    section_stats = {}  # Calculate stats for each section
    for section, grades in sections.items():
        grades_array = np.array(grades)  # Convert to numpy array
        letter_grades = [s['letter_grade'] for s in students if s.get(
            'section') == section and s.get('letter_grade')]

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


# Create histogram of grade distribution
def create_grade_distribution_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    grades = np.array([s['final_grade'] for s in students if s.get(
        'final_grade') is not None])  # Extract grades
    if len(grades) == 0:
        return None
    fig, ax = plt.subplots(figsize=figsize)  # Create figure
    ax.hist(grades, bins=15, alpha=0.7, color='#2E86AB',
            edgecolor='black')  # Histogram with 15 bins
    ax.set_xlabel('Grade', fontsize=7)
    ax.set_ylabel('Students', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


# Create bar chart of letter grade counts
def create_letter_grades_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    letter_grades = [s['letter_grade'] for s in students if s.get(
        'letter_grade')]  # Extract letter grades
    if not letter_grades:
        return None
    grade_counts = Counter(letter_grades)  # Count each grade
    grades = ['A', 'B', 'C', 'D', 'F']  # Grade order
    counts = [grade_counts.get(g, 0) for g in grades]  # Get counts
    colors = ['#2E86AB', '#A23B72', '#F18F01',
              '#C73E1D', '#3B1F2B']  # Colors for each grade
    fig, ax = plt.subplots(figsize=figsize)  # Create figure
    ax.bar(grades, counts, color=colors, alpha=0.7,
           edgecolor='black')  # Bar chart
    ax.set_xlabel('Grade', fontsize=7)
    ax.set_ylabel('Students', fontsize=7)
    ax.tick_params(labelsize=6)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


# Create a bar chart showing average score for each quiz
# This helps identify which quizzes were easier or harder
# Returns a matplotlib figure object
def create_quiz_performance_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    # Calculate quiz stats inline
    quiz_means = []  # Will store average score for each quiz
    quiz_labels = []  # Will store quiz names (quiz1, quiz2, etc)
    # Loop through all 5 quizzes
    for i in range(1, 6):
        quiz_key = f'quiz{i}'
        # Get all scores for this quiz (ignore None values)
        scores = [s[quiz_key] for s in students if s.get(quiz_key) is not None]
        # If this quiz has scores, calculate average
        if scores:
            quiz_means.append(np.mean(scores))
            quiz_labels.append(quiz_key)

    # If no quiz data available, return None
    if not quiz_means:
        return None

    # Convert means to numpy array
    means = np.array(quiz_means)
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    # Create bar chart with one bar per quiz
    ax.bar(range(len(quiz_labels)), means, alpha=0.7,
           color='#2E86AB', edgecolor='black')
    # Add axis labels
    ax.set_xlabel('Quiz', fontsize=7)
    ax.set_ylabel('Avg', fontsize=7)
    # Set x-axis tick positions
    ax.set_xticks(range(len(quiz_labels)))
    # Set x-axis labels (QUIZ1, QUIZ2, etc)
    ax.set_xticklabels([q.upper() for q in quiz_labels], fontsize=6)
    # Set y-axis range from 0 to 100
    ax.set_ylim(0, 100)
    # Set tick label size
    ax.tick_params(labelsize=6)
    # Add grid lines
    ax.grid(True, alpha=0.3)
    # Adjust layout
    plt.tight_layout()
    return fig  # Return the figure


# Create a box plot showing grade distribution
# Box plots show median, quartiles, and outliers in a compact visual
# The box shows the middle 50% of grades, whiskers show the range
# Returns a matplotlib figure object
def create_boxplot_chart(students: List[Dict[str, Any]], figsize=(3, 2)):
    # Extract all final grades into a numpy array
    grades = np.array([s['final_grade']
                      for s in students if s.get('final_grade') is not None])
    # If no grades available, return None
    if len(grades) == 0:
        return None
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    # Create box plot (vert=True means vertical, patch_artist allows coloring)
    box_plot = ax.boxplot(grades, vert=True, patch_artist=True)
    # Color the box blue
    box_plot['boxes'][0].set_facecolor('#2E86AB')
    # Add y-axis label
    ax.set_ylabel('Grade', fontsize=7)
    # Set tick label size
    ax.tick_params(labelsize=6)
    # Add grid lines
    ax.grid(True, alpha=0.3)
    # Adjust layout
    plt.tight_layout()
    return fig  # Return the figure


# Create a bar chart showing grade percentiles (25th, 50th, 75th, 90th, 95th)
# This shows what grade you need to be in the top X% of the class
# For example, 75th percentile shows the grade where 75% of students scored below
# Returns a matplotlib figure object
def create_percentiles_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    # Get percentile values from the data
    percentiles = get_grade_percentiles(students)
    # If no percentiles available, return None
    if not percentiles:
        return None

    # Define labels for each percentile
    labels = ['25th', '50th', '75th', '90th', '95th']
    # Get the grade value for each percentile
    values = [percentiles['p25'], percentiles['p50'], percentiles['p75'],
              percentiles['p90'], percentiles['p95']]
    # Define different colors for each bar
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    # Create bar chart with one bar per percentile
    bars = ax.bar(labels, values, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=1)
    # Add axis labels
    ax.set_ylabel('Grade', fontsize=8)
    ax.set_xlabel('Percentile', fontsize=8)
    # Set y-axis range from 0 to 100
    ax.set_ylim(0, 100)
    # Set tick label size
    ax.tick_params(labelsize=7)
    # Add grid lines on y-axis only
    ax.grid(True, alpha=0.3, axis='y')

    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()  # Get bar height (the grade value)
        # Add text label showing the exact grade value
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom', fontsize=7)

    # Adjust layout
    plt.tight_layout()
    return fig  # Return the figure


# Create a box plot chart to show outliers using the IQR (Interquartile Range) method
# This chart shows which grades are unusually high or low compared to the rest
# Red dashed lines show the bounds - anything outside is an outlier
# Returns a matplotlib figure object
def create_outliers_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    # Extract all final grades into a numpy array
    grades = np.array([s['final_grade']
                      for s in students if s.get('final_grade') is not None])
    # If no grades available, return None
    if len(grades) == 0:
        return None

    # Calculate outlier bounds using IQR method
    outlier_info = detect_outliers_iqr(grades.tolist())

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)

    # Create box plot showing grade distribution
    box_plot = ax.boxplot(grades, vert=True, patch_artist=True, widths=0.5)
    # Color the box blue
    box_plot['boxes'][0].set_facecolor('#2E86AB')
    box_plot['boxes'][0].set_alpha(0.7)

    # Get the outlier bounds
    # Grades below this are unusually low
    lower_bound = outlier_info['lower_bound']
    # Grades above this are unusually high
    upper_bound = outlier_info['upper_bound']

    # Add horizontal red dashed lines to show outlier bounds
    ax.axhline(y=lower_bound, color='red', linestyle='--', linewidth=1.5,
               label=f'Lower Bound: {lower_bound:.1f}')
    ax.axhline(y=upper_bound, color='red', linestyle='--', linewidth=1.5,
               label=f'Upper Bound: {upper_bound:.1f}')

    # Add labels and title
    ax.set_ylabel('Grade', fontsize=8)
    ax.set_title('Outlier Detection (IQR Method)',
                 fontsize=9, fontweight='bold')
    # Set tick label size
    ax.tick_params(labelsize=7)
    # Add legend showing what the red lines mean
    ax.legend(fontsize=6, loc='upper right')
    # Add grid lines on y-axis only
    ax.grid(True, alpha=0.3, axis='y')
    # Remove x-axis ticks (not needed for single box plot)
    ax.set_xticks([])

    # Adjust layout
    plt.tight_layout()
    return fig  # Return the figure


# Create a bar chart showing top 10 most improved students (midterm to final exam)
# This shows students who improved the most between midterm and final exam
# Each student has two bars - one for midterm score, one for final exam score
# Returns a matplotlib figure object
def create_most_improved_chart(students: List[Dict[str, Any]], figsize=(4, 3)):
    improvements = []

    # Calculate improvement for each student (final exam score minus midterm score)
    for student in students:
        midterm = student.get('midterm')
        final_exam = student.get('final')

        # Only include students who have both midterm and final exam scores
        if midterm is not None and final_exam is not None:
            improvement = final_exam - midterm  # Positive means they improved
            improvements.append({
                'student_id': student.get('student_id'),
                'first_name': student.get('first_name'),
                'last_name': student.get('last_name'),
                'midterm': midterm,
                'final_exam': final_exam,
                'improvement': improvement
            })

    # If no improvement data available, return None
    if not improvements:
        return None

    # Sort by improvement (highest first) and get top 10
    most_improved = sorted(
        improvements, key=lambda x: x['improvement'], reverse=True)[:10]

    # Prepare data for chart
    # Format: "J. Smith"
    names = [f"{s['first_name'][0]}. {s['last_name']}" for s in most_improved]
    midterms = [s['midterm'] for s in most_improved]  # Midterm scores
    final_exams = [s['final_exam'] for s in most_improved]  # Final exam scores
    improvements_vals = [s['improvement']
                         for s in most_improved]  # Improvement amounts

    # Set up x-axis positions for grouped bars
    x = np.arange(len(names))
    width = 0.35  # Width of each bar

    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    # Create two sets of bars - one for midterm, one for final exam
    bars1 = ax.bar(x - width/2, midterms, width, label='Midterm',
                   color='#A23B72', alpha=0.8, edgecolor='black', linewidth=0.8)
    bars2 = ax.bar(x + width/2, final_exams, width, label='Final Exam',
                   color='#6A994E', alpha=0.8, edgecolor='black', linewidth=0.8)

    # Add labels and title
    ax.set_ylabel('Grade', fontsize=8)
    ax.set_xlabel('Students', fontsize=8)
    ax.set_title('Top 10 Most Improved Students',
                 fontsize=9, fontweight='bold')
    # Set x-axis tick positions and labels
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=6)
    # Set y-axis range from 0 to 100
    ax.set_ylim(0, 100)
    # Set tick label size
    ax.tick_params(labelsize=7)
    # Add legend showing which bar is which
    ax.legend(fontsize=7)
    # Add grid lines on y-axis only
    ax.grid(True, alpha=0.3, axis='y')

    # Add improvement values on top of bars (shows how much they improved)
    for i, imp in enumerate(improvements_vals):
        # Place text above the taller bar
        ax.text(i, max(midterms[i], final_exams[i]) + 2, f'+{imp:.1f}',
                ha='center', va='bottom', fontsize=6, color='green', fontweight='bold')

    # Adjust layout
    plt.tight_layout()
    return fig  # Return the figure


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


class StudentAnalytics:  # Wrapper class for analytics functions
    # Initialize with student data
    def __init__(self, students: List[Dict[str, Any]]):
        self.students = students

    def get_final_grade_statistics(self):  # Get basic grade statistics
        return get_final_grade_stats(self.students)

    def get_section_comparison(self):  # Get section comparison stats
        return get_section_comparison(self.students)

    def get_percentiles(self):  # Get grade percentiles
        return get_grade_percentiles(self.students)

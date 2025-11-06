import matplotlib.pyplot as plt
import numpy as np
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter


class StudentAnalytics:
    def __init__(self, students: List[Dict[str, Any]]):
        self.students = students
        self.final_grades = [s['final_grade']
                             for s in students if s['final_grade'] is not None]

    def basic_statistics(self, data: List[float]) -> Dict[str, float]:
        """Calculate basic statistics for a dataset"""
        if not data:
            return {}

        return {
            'mean': np.mean(data),
            'median': np.median(data),
            'mode': self._calculate_mode(data),
            'std_dev': np.std(data),
            'variance': np.var(data),
            'min': min(data),
            'max': max(data),
            'range': max(data) - min(data)
        }

    def _calculate_mode(self, data: List[float]) -> float:
        """Calculate mode of a dataset"""
        if not data:
            return 0
        counter = Counter(data)
        mode = counter.most_common(1)[0][0]
        return mode

    def get_quiz_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all quizzes"""
        quiz_stats = {}
        for i in range(1, 6):
            quiz_key = f'quiz{i}'
            quiz_scores = [s[quiz_key]
                           for s in self.students if s.get(quiz_key) is not None]
            if quiz_scores:
                quiz_stats[quiz_key] = self.basic_statistics(quiz_scores)
        return quiz_stats

    def get_final_grade_statistics(self) -> Dict[str, float]:
        """Get statistics for final grades"""
        return self.basic_statistics(self.final_grades)

    def get_component_statistics(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all grade components"""
        components = ['quiz_avg', 'midterm', 'final', 'attendance_percent']
        component_stats = {}

        for comp in components:
            scores = [s[comp]
                      for s in self.students if s.get(comp) is not None]
            if scores:
                component_stats[comp] = self.basic_statistics(scores)

        return component_stats

    def calculate_percentiles(self) -> List[Dict[str, Any]]:
        """Calculate percentiles for each student's final grade"""
        if not self.final_grades:
            return []

        # Create student data with percentiles
        students_with_percentiles = []
        sorted_grades = sorted(self.final_grades)
        n = len(sorted_grades)

        for student in self.students:
            if student['final_grade'] is None:
                continue

            student_copy = student.copy()
            grade = student['final_grade']

            # Calculate percentile rank (percentage of scores below this score)
            below_count = sum(1 for g in sorted_grades if g < grade)
            percentile = (below_count / n) * 100

            student_copy['percentile'] = round(percentile, 2)
            student_copy['percentile_rank'] = below_count + \
                1  # Rank starting from 1

            students_with_percentiles.append(student_copy)

        return sorted(students_with_percentiles, key=lambda x: x['percentile'], reverse=True)

    def identify_outliers_iqr(self, data: List[float]) -> Tuple[List[float], Dict[str, float]]:
        """Identify outliers using IQR method"""
        if not data:
            return [], {}

        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [x for x in data if x < lower_bound or x > upper_bound]

        outlier_info = {
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': len(outliers)
        }

        return outliers, outlier_info

    def identify_outliers_zscore(self, data: List[float], threshold: float = 2.0) -> Tuple[List[float], Dict[str, float]]:
        """Identify outliers using Z-score method"""
        if not data:
            return [], {}

        mean = np.mean(data)
        std_dev = np.std(data)

        if std_dev == 0:  # All values are the same
            return [], {'mean': mean, 'std_dev': std_dev, 'threshold': threshold}

        z_scores = [(x - mean) / std_dev for x in data]
        outliers = [data[i]
                    for i, z in enumerate(z_scores) if abs(z) > threshold]

        outlier_info = {
            'mean': mean,
            'std_dev': std_dev,
            'threshold': threshold,
            'outlier_count': len(outliers)
        }

        return outliers, outlier_info

    def get_all_outliers(self) -> Dict[str, Any]:
        """Identify outliers in final grades using both methods"""
        if not self.final_grades:
            return {}

        iqr_outliers, iqr_info = self.identify_outliers_iqr(self.final_grades)
        zscore_outliers, zscore_info = self.identify_outliers_zscore(
            self.final_grades)

        # Get student info for outliers
        iqr_outlier_students = []
        for grade in iqr_outliers:
            for student in self.students:
                if student['final_grade'] == grade:
                    iqr_outlier_students.append({
                        'student_id': student['student_id'],
                        'name': f"{student['first_name']} {student['last_name']}",
                        'final_grade': grade,
                        'section': student['section'],
                        'method': 'IQR'
                    })
                    break

        zscore_outlier_students = []
        for grade in zscore_outliers:
            for student in self.students:
                if student['final_grade'] == grade:
                    zscore_outlier_students.append({
                        'student_id': student['student_id'],
                        'name': f"{student['first_name']} {student['last_name']}",
                        'final_grade': grade,
                        'section': student['section'],
                        'method': 'Z-Score'
                    })
                    break

        return {
            'iqr': {
                'outliers': iqr_outliers,
                'outlier_students': iqr_outlier_students,
                'statistics': iqr_info
            },
            'zscore': {
                'outliers': zscore_outliers,
                'outlier_students': zscore_outlier_students,
                'statistics': zscore_info
            },
            'all_outlier_students': iqr_outlier_students + zscore_outlier_students
        }

    def get_section_comparison(self) -> Dict[str, Dict[str, Any]]:
        """Compare statistics between sections"""
        sections = {}

        for student in self.students:
            section = student.get('section')
            final_grade = student.get('final_grade')

            if section and final_grade is not None:
                if section not in sections:
                    sections[section] = []
                sections[section].append(final_grade)

        section_stats = {}
        for section, grades in sections.items():
            section_stats[section] = {
                'statistics': self.basic_statistics(grades),
                'count': len(grades),
                'letter_grades': self._get_section_letter_grades(section)
            }

        return section_stats

    def _get_section_letter_grades(self, section: str) -> Dict[str, int]:
        """Get letter grade distribution for a section"""
        section_students = [s for s in self.students if s.get(
            'section') == section and s.get('letter_grade')]
        letter_counts = Counter(student['letter_grade']
                                for student in section_students)
        return dict(letter_counts)

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analytics report"""
        return {
            'final_grade_statistics': self.get_final_grade_statistics(),
            'quiz_statistics': self.get_quiz_statistics(),
            'component_statistics': self.get_component_statistics(),
            'percentiles': self.calculate_percentiles(),
            'outliers': self.get_all_outliers(),
            'section_comparison': self.get_section_comparison(),
            'total_students': len([s for s in self.students if s['final_grade'] is not None]),
            'students_with_missing_data': len([s for s in self.students if s['final_grade'] is None])
        }


class GradeVisualizer:
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']

    def plot_statistics_summary(self, analytics: StudentAnalytics, save_path: str = None):
        """Plot summary statistics for final grades"""
        stats = analytics.get_final_grade_statistics()

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        # Central tendency
        tendency_metrics = ['mean', 'median', 'mode']
        tendency_values = [stats[metric] for metric in tendency_metrics]
        bars1 = ax1.bar(tendency_metrics, tendency_values,
                        color=self.colors[:3], alpha=0.7)
        ax1.set_title('Central Tendency Measures')
        ax1.set_ylabel('Grade')
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}', ha='center', va='bottom')

        # Variability
        variability_metrics = ['std_dev', 'variance', 'range']
        variability_values = [stats[metric] for metric in variability_metrics]
        bars2 = ax2.bar(variability_metrics, variability_values,
                        color=self.colors[1:4], alpha=0.7)
        ax2.set_title('Variability Measures')
        ax2.set_ylabel('Grade Points')
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}', ha='center', va='bottom')

        # Distribution shape
        final_grades = [s['final_grade']
                        for s in analytics.students if s['final_grade'] is not None]
        ax3.hist(final_grades, bins=15, alpha=0.7,
                 color=self.colors[0], edgecolor='black', density=True)
        ax3.axvline(stats['mean'], color='red', linestyle='--',
                    label=f'Mean: {stats["mean"]:.1f}')
        ax3.axvline(stats['median'], color='green',
                    linestyle='--', label=f'Median: {stats["median"]:.1f}')
        ax3.set_xlabel('Final Grade')
        ax3.set_ylabel('Density')
        ax3.set_title('Grade Distribution with Mean/Median')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Box plot showing outliers
        outlier_data = analytics.get_all_outliers()
        box_plot = ax4.boxplot(final_grades, vert=True, patch_artist=True)
        box_plot['boxes'][0].set_facecolor(self.colors[0])
        ax4.set_ylabel('Final Grade')
        ax4.set_title(
            f'Box Plot (Outliers: {outlier_data["iqr"]["statistics"]["outlier_count"]})')
        ax4.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(
                save_path, 'statistics_summary.png'), dpi=300, bbox_inches='tight')
        plt.show()

    def plot_percentile_analysis(self, analytics: StudentAnalytics, save_path: str = None):
        """Visualize percentile rankings"""
        students_with_percentiles = analytics.calculate_percentiles()

        percentiles = [s['percentile'] for s in students_with_percentiles]
        final_grades = [s['final_grade'] for s in students_with_percentiles]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Percentile vs Final Grade
        scatter = ax1.scatter(percentiles, final_grades,
                              alpha=0.6, color=self.colors[0])
        ax1.set_xlabel('Percentile Rank')
        ax1.set_ylabel('Final Grade')
        ax1.set_title('Final Grade vs Percentile Rank')
        ax1.grid(True, alpha=0.3)

        # Percentile distribution
        ax2.hist(percentiles, bins=10, alpha=0.7,
                 color=self.colors[1], edgecolor='black')
        ax2.set_xlabel('Percentile')
        ax2.set_ylabel('Number of Students')
        ax2.set_title('Distribution of Percentile Ranks')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(
                save_path, 'percentile_analysis.png'), dpi=300, bbox_inches='tight')
        plt.show()

    def plot_outlier_analysis(self, analytics: StudentAnalytics, save_path: str = None):
        """Visualize outlier detection using different methods"""
        outlier_data = analytics.get_all_outliers()
        final_grades = [s['final_grade']
                        for s in analytics.students if s['final_grade'] is not None]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # IQR Method
        iqr_stats = outlier_data['iqr']['statistics']
        ax1.boxplot(final_grades, vert=True)
        ax1.axhline(iqr_stats['upper_bound'], color='red',
                    linestyle='--', label='Upper Bound')
        ax1.axhline(iqr_stats['lower_bound'], color='red',
                    linestyle='--', label='Lower Bound')
        ax1.set_title(
            f'IQR Method: {outlier_data["iqr"]["statistics"]["outlier_count"]} outliers')
        ax1.set_ylabel('Final Grade')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Z-score Method
        zscore_stats = outlier_data['zscore']['statistics']
        z_scores = [(x - zscore_stats['mean']) / zscore_stats['std_dev']
                    for x in final_grades]
        ax2.scatter(range(len(z_scores)), z_scores,
                    alpha=0.6, color=self.colors[1])
        ax2.axhline(zscore_stats['threshold'], color='red', linestyle='--',
                    label=f'Threshold: ±{zscore_stats["threshold"]}')
        ax2.axhline(-zscore_stats['threshold'], color='red', linestyle='--')
        ax2.set_xlabel('Student Index')
        ax2.set_ylabel('Z-Score')
        ax2.set_title(
            f'Z-Score Method: {outlier_data["zscore"]["statistics"]["outlier_count"]} outliers')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(save_path, 'outlier_analysis.png'),
                        dpi=300, bbox_inches='tight')
        plt.show()

        # Print outlier details
        print("\n=== OUTLIER ANALYSIS ===")
        print(
            f"IQR Method found {len(outlier_data['iqr']['outlier_students'])} outliers")
        print(
            f"Z-Score Method found {len(outlier_data['zscore']['outlier_students'])} outliers")

        if outlier_data['iqr']['outlier_students']:
            print("\nIQR Outliers:")
            for student in outlier_data['iqr']['outlier_students']:
                print(
                    f"  {student['name']} (Section {student['section']}): {student['final_grade']:.1f}")

    def plot_quiz_statistics(self, analytics: StudentAnalytics, save_path: str = None):
        """Plot detailed quiz statistics"""
        quiz_stats = analytics.get_quiz_statistics()

        quizzes = list(quiz_stats.keys())
        means = [quiz_stats[quiz]['mean'] for quiz in quizzes]
        std_devs = [quiz_stats[quiz]['std_dev'] for quiz in quizzes]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Quiz means with error bars
        x_pos = np.arange(len(quizzes))
        bars = ax1.bar(x_pos, means, yerr=std_devs, capsize=5, alpha=0.7,
                       color=self.colors[0], edgecolor='black')
        ax1.set_xlabel('Quiz')
        ax1.set_ylabel('Average Score')
        ax1.set_title('Quiz Performance with Standard Deviation')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels([q.upper() for q in quizzes])
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)

        # Add value labels
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                     f'{mean:.1f}', ha='center', va='bottom')

        # Quiz difficulty comparison (inverse of mean)
        difficulty = [100 - mean for mean in means]  # Higher = more difficult
        ax2.bar(x_pos, difficulty, alpha=0.7,
                color=self.colors[1], edgecolor='black')
        ax2.set_xlabel('Quiz')
        ax2.set_ylabel('Difficulty Index (100 - Mean)')
        ax2.set_title('Relative Quiz Difficulty')
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels([q.upper() for q in quizzes])
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(save_path, 'quiz_statistics.png'),
                        dpi=300, bbox_inches='tight')
        plt.show()

    def plot_grade_distribution(self, students: List[Dict[str, Any]], save_path: str = None):
        """Plot histogram of final grade distribution"""
        final_grades = [s['final_grade']
                        for s in students if s['final_grade'] is not None]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        # Histogram
        ax1.hist(final_grades, bins=20, alpha=0.7,
                 color=self.colors[0], edgecolor='black')
        ax1.set_xlabel('Final Grade')
        ax1.set_ylabel('Number of Students')
        ax1.set_title('Distribution of Final Grades')
        ax1.grid(True, alpha=0.3)

        # Box plot
        ax2.boxplot(final_grades, vert=False)
        ax2.set_xlabel('Final Grade')
        ax2.set_title('Grade Distribution Box Plot')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(
                save_path, 'grade_distribution.png'), dpi=300, bbox_inches='tight')
        plt.show()

    def plot_letter_grades(self, students: List[Dict[str, Any]], save_path: str = None):
        """Plot bar chart of letter grade counts"""
        letter_grades = [s['letter_grade']
                         for s in students if s['letter_grade']]
        grade_counts = {}

        for grade in ['A', 'B', 'C', 'D', 'F']:
            grade_counts[grade] = letter_grades.count(grade)

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(grade_counts.keys(), grade_counts.values(),
                      color=self.colors, alpha=0.7, edgecolor='black')

        ax.set_xlabel('Letter Grade')
        ax.set_ylabel('Number of Students')
        ax.set_title('Distribution of Letter Grades')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')

        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        if save_path:
            plt.savefig(os.path.join(save_path, 'letter_grades.png'),
                        dpi=300, bbox_inches='tight')
        plt.show()

    def generate_all_analytical_visualizations(self, students: List[Dict[str, Any]], output_folder: str = None):
        """Generate all analytics visualizations"""
        if output_folder and not os.path.exists(output_folder):
            os.makedirs(output_folder)

        analytics = StudentAnalytics(students)

        print("Generating analytical visualizations...")
        self.plot_statistics_summary(analytics, output_folder)
        self.plot_percentile_analysis(analytics, output_folder)
        self.plot_outlier_analysis(analytics, output_folder)
        self.plot_quiz_statistics(analytics, output_folder)
        self.plot_grade_distribution(students, output_folder)
        self.plot_letter_grades(students, output_folder)

        # Generate and print comprehensive report
        report = analytics.generate_comprehensive_report()
        self._print_analytics_report(report)

        print("All analytical visualizations completed!")

    def _print_analytics_report(self, report: Dict[str, Any]):
        """Print a text-based analytics report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE ANALYTICS REPORT")
        print("="*60)

        print(f"\nTotal Students: {report['total_students']}")
        print(
            f"Students with Missing Data: {report['students_with_missing_data']}")

        print("\nFINAL GRADE STATISTICS:")
        stats = report['final_grade_statistics']
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value:.2f}")

        print(f"\nOUTLIER ANALYSIS:")
        print(
            f"  IQR Method: {report['outliers']['iqr']['statistics']['outlier_count']} outliers")
        print(
            f"  Z-Score Method: {report['outliers']['zscore']['statistics']['outlier_count']} outliers")

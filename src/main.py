from ingest import ingest
from transform import transform_students, load_config
from reports import ReportGenerator
from analyze import StudentAnalytics, GradeVisualizer

# Load data
students = ingest()
students = transform_students(students)
config = load_config()

# Generate reports
generator = ReportGenerator(students, config)

# Save all reports (this also prints the summary)
output_folder = config.get('path', {}).get('output_folder', 'data/output')
generator.save_all_reports(output_folder)

# Generate analytics
print("GENERATING ANALYTICS AND VISUALIZATIONS")

analytics = StudentAnalytics(students)
visualizer = GradeVisualizer()

# Generate comprehensive analytics report
report = analytics.generate_comprehensive_report()
visualizer._print_analytics_report(report)

# Generate all visualizations
visualizer.generate_all_analytical_visualizations(students, output_folder)



from ingest import ingest
from transform import transform_students, load_config

# Load data
students = ingest()
students = transform_students(students)
config = load_config()

# Generate reports
generator = ReportGenerator(students, config)

# Print summary to console
print(generator.generate_summary_report())

# Save all reports
output_folder = config.get('path', {}).get('output_folder', 'data/output')
generator.save_all_reports(output_folder)

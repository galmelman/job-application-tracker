import csv
import sqlite3
from models import JobApplication
from database import create_table, insert_application

def migrate_csv_to_sqlite(csv_filename, db_filename):
    # Create the SQLite table
    create_table()

    # Connect to the SQLite database
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    # Read the CSV file and insert data into SQLite
    with open(csv_filename, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  # Skip the header row

        for row in csv_reader:
            company, position, date_applied, status, notes, reminder_date = row
            app = JobApplication(company, position, date_applied, status, notes, reminder_date)
            insert_application(app)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f"Migration from {csv_filename} to {db_filename} completed successfully.")

if __name__ == "__main__":
    csv_filename = "job_applications.csv"
    db_filename = "job_applications.db"
    migrate_csv_to_sqlite(csv_filename, db_filename)
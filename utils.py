import csv
from models import JobApplication

def save_applications(filename, applications):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Company", "Position", "Date Applied", "Status", "Notes"])
        for app in applications:
            writer.writerow([app.company, app.position, app.date_applied, app.status, app.notes])

def load_applications(filename):
    applications = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                applications.append(JobApplication(*row))
    except FileNotFoundError:
        pass
    return applications

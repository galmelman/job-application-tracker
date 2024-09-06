import sqlite3
from models import JobApplication

def create_table():
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY,
                  company TEXT,
                  position TEXT,
                  date_applied TEXT,
                  status TEXT,
                  notes TEXT,
                  reminder_date TEXT)''')
    conn.commit()
    conn.close()

def insert_application(app):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''INSERT INTO applications
                 (company, position, date_applied, status, notes, reminder_date)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date))
    conn.commit()
    conn.close()

def update_application(app_id, app):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''UPDATE applications
                 SET company=?, position=?, date_applied=?, status=?, notes=?, reminder_date=?
                 WHERE id=?''',
              (app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date, app_id))
    conn.commit()
    conn.close()

def delete_application(app_id):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('DELETE FROM applications WHERE id=?', (app_id,))
    conn.commit()
    conn.close()

def get_all_applications():
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('SELECT * FROM applications')
    rows = c.fetchall()
    applications = []
    for row in rows:
        app = JobApplication(row[1], row[2], row[3], row[4], row[5], row[6])
        app.id = row[0]
        applications.append(app)
    conn.close()
    return applications

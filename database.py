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
                  reminder_date TEXT,
                  location TEXT,
                  application_submitted TEXT,
                  resume_screened TEXT,
                  phone_interview TEXT,
                  technical_interview TEXT,
                  onsite_interview TEXT,
                  offer_received TEXT,
                  offer_accepted TEXT,
                  offer_rejected TEXT,
                  salary_offered REAL,
                  job_description TEXT,
                  company_culture TEXT,
                  interviewer_names TEXT,
                  follow_up_dates TEXT)''')
    conn.commit()
    conn.close()

def insert_application(app):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''INSERT INTO applications
                 (company, position, date_applied, status, notes, reminder_date, location,
                  application_submitted, resume_screened, phone_interview, technical_interview,
                  onsite_interview, offer_received, offer_accepted, offer_rejected,
                  salary_offered, job_description, company_culture, interviewer_names, follow_up_dates)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date, app.location,
               app.application_submitted, app.resume_screened, app.phone_interview, app.technical_interview,
               app.onsite_interview, app.offer_received, app.offer_accepted, app.offer_rejected,
               app.salary_offered, app.job_description, app.company_culture, app.interviewer_names,
               ','.join(app.follow_up_dates)))
    conn.commit()
    conn.close()


def update_application(app_id, app):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''UPDATE applications
                 SET company=?, position=?, date_applied=?, status=?, notes=?, reminder_date=?, location=?, 
                 application_submitted=?, resume_screened=?, phone_interview=?,
                 technical_interview=?, onsite_interview=?, offer_received=?, offer_accepted=?, offer_rejected=?,
                 salary_offered=?, job_description=?, company_culture=?, interviewer_names=?,
                 follow_up_dates=?
                 WHERE id=?''',
              (app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date, app.location,
               app.application_submitted, app.resume_screened, app.phone_interview,
               app.technical_interview, app.onsite_interview, app.offer_received, app.offer_accepted, app.offer_rejected,
               app.salary_offered, app.job_description, app.company_culture, app.interviewer_names,
               ','.join(app.follow_up_dates),
               app_id))
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
        app = JobApplication(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        app.id = row[0]
        app.application_submitted = row[8]
        app.resume_screened = row[9]
        app.phone_interview = row[10]
        app.technical_interview = row[11]
        app.onsite_interview = row[12]
        app.offer_received = row[13]
        app.offer_accepted = row[14]
        app.offer_rejected = row[15]
        app.salary_offered = row[16]
        app.job_description = row[17]
        app.company_culture = row[18]
        app.interviewer_names = row[19]
        app.follow_up_dates = row[20].split(',') if row[20] else []
        applications.append(app)
    conn.close()
    return applications

def get_application_by_id(app_id):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('SELECT * FROM applications WHERE id=?', (app_id,))
    row = c.fetchone()
    if row:
        app = JobApplication(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        app.id = row[0]
        app.application_submitted = row[8]
        app.resume_screened = row[9]
        app.phone_interview = row[10]
        app.technical_interview = row[11]
        app.onsite_interview = row[12]
        app.offer_received = row[13]
        app.offer_accepted = row[14]
        app.offer_rejected = row[15]
        app.salary_offered = row[16]
        app.job_description = row[17]
        app.company_culture = row[18]
        app.interviewer_names = row[19]
        app.follow_up_dates = row[20].split(',') if row[20] else []
        conn.close()
        return app
    conn.close()
    return None

from datetime import datetime


class JobApplication:
    def __init__(self, company, position, date_applied, status="Applied", notes="", reminder_date="", location=""):
        self.id = None
        self.company = company
        self.position = position
        self.date_applied = date_applied
        self.status = status
        self.notes = notes
        self.reminder_date = reminder_date
        self.location = location

        # New fields for tracking application process
        self.application_submitted = date_applied
        self.resume_screened = None
        self.phone_interview = None
        self.technical_interview = None
        self.onsite_interview = None
        self.offer_received = None
        self.offer_accepted = None
        self.offer_rejected = None
        self.salary_offered = None
        self.job_description = ""
        self.company_culture = ""
        self.interviewer_names = ""
        self.follow_up_dates = []

    def update_status(self, new_status, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.status = new_status
        setattr(self, new_status.lower().replace(" ", "_"), date)

    def add_follow_up(self, date):
        self.follow_up_dates.append(date)

    def __str__(self):
        return f"{self.company}, {self.position}, {self.status}, Applied: {self.date_applied}"

class JobApplication:
    def __init__(self, company, position, date_applied, status="Applied", notes="", reminder_date=""):
        self.company = company
        self.position = position
        self.date_applied = date_applied
        self.status = status
        self.notes = notes
        self.reminder_date = reminder_date

    def __str__(self):
        return f"{self.company}, {self.position}, {self.date_applied}, {self.status}, {self.notes}, {self.reminder_date}"

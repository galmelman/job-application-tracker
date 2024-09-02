class JobApplication:
    def __init__(self, company, position, date_applied, status="Applied", notes=""):
        self.company = company
        self.position = position
        self.date_applied = date_applied
        self.status = status
        self.notes = notes
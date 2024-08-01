import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class JobApplication:
    def __init__(self, company, position, date_applied, status="Applied", notes=""):
        self.company = company
        self.position = position
        self.date_applied = date_applied
        self.status = status
        self.notes = notes



class ApplicationTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Application Tracker")
        self.master.geometry("900x600")

        self.applications = []
        self.filename = "job_applications.csv"
        self.load_applications()

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Company:").grid(row=0, column=0, sticky=tk.W)
        self.company_entry = ttk.Entry(input_frame)
        self.company_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Position:").grid(row=0, column=2, sticky=tk.W)
        self.position_entry = ttk.Entry(input_frame)
        self.position_entry.grid(row=0, column=3)

        ttk.Label(input_frame, text="Date Applied (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W)
        self.date_applied_entry = ttk.Entry(input_frame)
        self.date_applied_entry.grid(row=1, column=1)

        ttk.Label(input_frame, text="Status:").grid(row=1, column=2, sticky=tk.W)
        self.status_combo = ttk.Combobox(input_frame, values=["Applied", "Interview Scheduled", "Offer Received", "Rejected", "Withdrawn"])
        self.status_combo.grid(row=1, column=3)
        self.status_combo.set("Applied")

        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, sticky=tk.W)
        self.notes_entry = ttk.Entry(input_frame)
        self.notes_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW)

        ttk.Button(input_frame, text="Add/Update Application", command=self.add_or_update_application).grid(row=3, column=1, columnspan=2, pady=10)

        # Table
        self.tree = ttk.Treeview(self.master, columns=("Company", "Position", "Date Applied", "Status", "Notes"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.heading("Company", text="Company")
        self.tree.heading("Position", text="Position")
        self.tree.heading("Date Applied", text="Date Applied")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Notes", text="Notes")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons Frame
        button_frame = ttk.Frame(self.master, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        self.update_table()

    def add_or_update_application(self):
        company = self.company_entry.get()
        position = self.position_entry.get()
        date_applied = self.date_applied_entry.get()
        status = self.status_combo.get()
        notes = self.notes_entry.get()

        if company and position:
            if not date_applied:
                date_applied = datetime.now().strftime("%Y-%m-%d")
            selected_items = self.tree.selection()
            if selected_items:
                # Update existing application
                item = selected_items[0]
                index = self.tree.index(item)
                self.applications[index].company = company
                self.applications[index].position = position
                self.applications[index].date_applied = date_applied
                self.applications[index].status = status
                self.applications[index].notes = notes
            else:
                # Add new application
                new_app = JobApplication(company, position, date_applied, status, notes)
                self.applications.append(new_app)

            self.save_applications()
            self.update_table()
            self.clear_entries()
        else:
            messagebox.showwarning("Input Error", "Company and Position are required fields.")

    def edit_selected(self):
        selected_items = self.tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.tree.item(item)['values']
            self.company_entry.delete(0, tk.END)
            self.company_entry.insert(0, values[0])
            self.position_entry.delete(0, tk.END)
            self.position_entry.insert(0, values[1])
            self.date_applied_entry.delete(0, tk.END)
            self.date_applied_entry.insert(0, values[2])
            self.status_combo.set(values[3])
            self.notes_entry.delete(0, tk.END)
            self.notes_entry.insert(0, values[4])

        else:
            messagebox.showinfo("Selection", "Please select an application to edit.")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if selected_items:
            if messagebox.askyesno("Delete", "Are you sure you want to delete the selected application?"):
                item = selected_items[0]
                index = self.tree.index(item)
                del self.applications[index]
                self.save_applications()
                self.update_table()
        else:
            messagebox.showinfo("Selection", "Please select an application to delete.")

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for app in self.applications:
            self.tree.insert("", "end", values=(app.company, app.position, app.date_applied, app.status, app.notes))

    def clear_entries(self):
        self.company_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)
        self.date_applied_entry.delete(0, tk.END)
        self.status_combo.set("Applied")
        self.notes_entry.delete(0, tk.END)

    def save_applications(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Company", "Position", "Date Applied", "Status", "Notes"])
            for app in self.applications:
                writer.writerow([app.company, app.position, app.date_applied, app.status, app.notes])

    def load_applications(self):
        try:
            with open(self.filename, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    self.applications.append(JobApplication(*row))
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationTracker(root)
    root.mainloop()
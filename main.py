import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
import re


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
        self.master.geometry("1000x700")

        self.applications = []
        self.filename = "job_applications.csv"
        self.load_applications()

        self.status_colors = {
            "Applied": "#FFD700",  # Gold
            "Interview Scheduled": "#87CEEB",  # Sky Blue
            "Offer Received": "#90EE90",  # Light Green
            "Rejected": "#FFA07A",  # Light Salmon
            "Withdrawn": "#D3D3D3"  # Light Gray
        }

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Application Details", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # Company
        ttk.Label(input_frame, text="Company:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.company_entry = ttk.Entry(input_frame, width=30)
        self.company_entry.grid(row=0, column=1, pady=2)

        # Position
        ttk.Label(input_frame, text="Position:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.position_entry = ttk.Entry(input_frame, width=30)
        self.position_entry.grid(row=0, column=3, pady=2)

        # Date Applied
        ttk.Label(input_frame, text="Date Applied (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_applied_entry = ttk.Entry(input_frame, width=30)
        self.date_applied_entry.grid(row=1, column=1, pady=2)

        # Status
        ttk.Label(input_frame, text="Status:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.status_combo = ttk.Combobox(input_frame, values=list(self.status_colors.keys()), width=28)
        self.status_combo.grid(row=1, column=3, pady=2)
        self.status_combo.set("Applied")

        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.notes_entry = ttk.Entry(input_frame, width=90)
        self.notes_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=2)

        # Add/Update Button
        ttk.Button(input_frame, text="Add/Update Application", command=self.add_or_update_application).grid(row=3,
                                                                                                            column=1,
                                                                                                            columnspan=2,
                                                                                                            pady=10)

        # Table Frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=("Company", "Position", "Date Applied", "Status", "Notes"),
                                 show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Treeview Headings
        for col in ("Company", "Position", "Date Applied", "Status", "Notes"):
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
            self.tree.column(col, width=100)

        # Buttons Frame
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        self.update_table()

    def add_or_update_application(self):
        company = self.company_entry.get().strip()
        position = self.position_entry.get().strip()
        date_applied = self.date_applied_entry.get().strip()
        status = self.status_combo.get()
        notes = self.notes_entry.get().strip()

        if not company or not position:
            messagebox.showwarning("Input Error", "Company and Position are required fields.")
            return

        if not self.validate_date(date_applied):
            messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        selected_items = self.tree.selection()
        if selected_items:
            # Update existing application
            item = selected_items[0]
            index = self.tree.index(item)
            self.applications[index] = JobApplication(company, position, date_applied, status, notes)
        else:
            # Add new application
            new_app = JobApplication(company, position, date_applied, status, notes)
            self.applications.append(new_app)

        self.save_applications()
        self.update_table()
        self.clear_entries()

    def validate_date(self, date_string):
        if not date_string:
            return True  # Allow empty date
        pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        if not pattern.match(date_string):
            return False
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

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
            item = self.tree.insert("", "end",
                                    values=(app.company, app.position, app.date_applied, app.status, app.notes))
            self.tree.item(item, tags=(app.status,))

        # Configure tag colors
        for status, color in self.status_colors.items():
            self.tree.tag_configure(status, background=color)

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

    def sort_treeview(self, col, reverse):
        # Get all item IDs and their values for the specified column
        items = [(self.tree.set(item_id, col), item_id) for item_id in self.tree.get_children('')]

        # Sort items based on column values
        items.sort(reverse=reverse)

        # Rearrange items in the Treeview
        for index, (value, item_id) in enumerate(items):
            self.tree.move(item_id, '', index)

        # Update column header to toggle sort order on click
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))


if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationTracker(root)
    root.mainloop()
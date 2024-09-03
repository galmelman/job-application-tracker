import tkinter as tk
from tkinter import ttk
from utils import save_applications, load_applications
from controllers import add_or_update_application, edit_selected, delete_selected


class ApplicationTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Application Tracker")
        self.master.geometry("1000x700")

        self.applications = load_applications("job_applications.csv")
        self.filename = "job_applications.csv"
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


        # reminder Date
        ttk.Label(input_frame, text="Reminder Date (YYYY-MM-DD").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.reminder_date_entry = ttk.Entry(input_frame, width=90)
        self.reminder_date_entry.grid(row=3, column=1, columnspan=3, pady=2)


        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.notes_entry = ttk.Entry(input_frame, width=90)
        self.notes_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=2)



        # Add/Update Button
        ttk.Button(input_frame, text="Add Application", command=self.add_or_update_application).grid(row=4,
                                                                                                            column=1,
                                                                                                            columnspan=2,
                                                                                                            pady=10)

        # Table Frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=("Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date (YYYY-MM-DD"),
                                 show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)


        # Treeview Headings
        for col in ("Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date (YYYY-MM-DD"):
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
            self.tree.column(col, width=100)

        # Buttons Frame
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.LEFT, padx=5)

        self.update_table()

    def add_or_update_application(self):
        add_or_update_application(
            self.applications,
            self.tree,
            self.company_entry,
            self.position_entry,
            self.date_applied_entry,
            self.status_combo,
            self.notes_entry,
            self.reminder_date_entry,
            self.save_applications,
            self.update_table,
            self.clear_entries
        )

    def edit_selected(self):
        edit_selected(
            self.tree,
            self.company_entry,
            self.position_entry,
            self.date_applied_entry,
            self.status_combo,
            self.notes_entry,
            self.reminder_date_entry
        )

    def delete_selected(self):
        delete_selected(
            self.tree,
            self.applications,
            self.save_applications,
            self.update_table
        )

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for app in self.applications:
            item = self.tree.insert("", "end",
                                    values=(app.company, app.position, app.date_applied, app.status, app.notes,app.reminder_date))
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
        self.reminder_date_entry.delete(0, tk.END)

    def save_applications(self):
        save_applications(self.filename, self.applications)

    def load_applications(self):
        self.applications = load_applications(self.filename)

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

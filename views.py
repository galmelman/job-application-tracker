import tkinter as tk
from tkinter import ttk
from database import get_all_applications, create_table
from controllers import add_or_update_application, edit_selected, delete_selected
from utils import get_application_statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ApplicationTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Job Application Tracker")
        self.master.geometry("1000x700")

        create_table()  # Create the SQLite table if it doesn't exist
        self.applications = get_all_applications()
        self.status_colors = {
            "Applied": "#FFD700",  # Gold
            "Interview Scheduled": "#87CEEB",  # Sky Blue
            "Offer Received": "#90EE90",  # Light Green
            "Rejected": "#FFA07A",  # Light Salmon
            "Withdrawn": "#D3D3D3",  # Light Gray
            "Awaiting Response": "#FFFACD"  # Lemon Chiffon

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

        # Reminder Date
        ttk.Label(input_frame, text="Reminder Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.reminder_date_entry = ttk.Entry(input_frame, width=90)
        self.reminder_date_entry.grid(row=3, column=1, columnspan=3, pady=2)

        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.notes_entry = ttk.Entry(input_frame, width=90)
        self.notes_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=2)

        # Add/Update Button
        ttk.Button(input_frame, text="Add/Update Application", command=self.add_or_update_application).grid(row=4,
                                                                                                            column=1,
                                                                                                            columnspan=2,
                                                                                                            pady=10)

        # Table Frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date"),
                                 show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Treeview Headings
        for col in ("ID", "Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date"):
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
            self.tree,
            self.company_entry,
            self.position_entry,
            self.date_applied_entry,
            self.status_combo,
            self.notes_entry,
            self.reminder_date_entry,
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
        delete_selected(self.tree, self.update_table)

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.applications = get_all_applications()
        for app in self.applications:
            item = self.tree.insert("", "end",
                                    values=(app.id, app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date))
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


def create_analytics_frame(master, applications):
    frame = ttk.Frame(master)
    frame.pack(fill=tk.BOTH, expand=True)

    # Get statistics from the applications
    stats = get_application_statistics()

    # Create a Pie Chart for Application Statuses
    statuses = stats['applications_per_status']
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))

    # Pie Chart
    ax[0].pie(statuses.values(), labels=statuses.keys(), autopct='%1.1f%%', startangle=90)
    ax[0].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax[0].set_title('Application Statuses')

    # Bar Chart for Applications per Month
    applications_per_month = stats['applications_per_month']
    months = [str(month) for month in applications_per_month.keys()]  # Convert Period objects to strings
    counts = list(applications_per_month.values())

    ax[1].bar(months, counts)
    ax[1].set_xticklabels(months, rotation=45)
    ax[1].set_title('Applications per Month')
    ax[1].set_xlabel('Month')
    ax[1].set_ylabel('Number of Applications')

    # Embed the charts in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    return frame
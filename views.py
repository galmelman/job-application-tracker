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
            "Awaiting Response": "#00CED1"  # Dark Turquoise
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
        self.tree = ttk.Treeview(table_frame, columns=(
        "ID", "Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date"),
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
        ttk.Button(button_frame, text="View Analytics", command=self.open_analytics_window).pack(side=tk.LEFT, padx=5)

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
                                    values=(app.id, app.company, app.position, app.date_applied, app.status, app.notes,
                                            app.reminder_date))
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
        items = [(self.tree.set(item_id, col), item_id) for item_id in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (value, item_id) in enumerate(items):
            self.tree.move(item_id, '', index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def open_analytics_window(self):
        analytics_window = tk.Toplevel(self.master)
        analytics_window.title("Application Analytics")
        analytics_window.geometry("1000x800")
        AnalyticsView(analytics_window, self.applications)


class AnalyticsView:
    def __init__(self, master, applications):
        self.master = master
        self.applications = applications
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.master)
        frame.pack(fill=tk.BOTH, expand=True)

        stats = get_application_statistics()

        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Pie Chart for Application Statuses
        self.create_status_chart(notebook, stats)

        # Bar Chart for Applications per Month
        self.create_month_chart(notebook, stats)

        # Bar Chart for Applications per Company
        self.create_company_chart(notebook, stats)

        # Bar Chart for Applications per Position
        self.create_position_chart(notebook, stats)

        # Text widget for additional statistics
        self.create_text_stats(notebook, stats)

    def create_status_chart(self, notebook, stats):
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="Application Statuses")

        statuses = stats['applications_per_status']
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(statuses.values(), labels=statuses.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Application Statuses')

        canvas = FigureCanvasTkAgg(fig, master=status_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_month_chart(self, notebook, stats):
        month_frame = ttk.Frame(notebook)
        notebook.add(month_frame, text="Applications per Month")

        applications_per_month = stats['applications_per_month']
        months = [str(month) for month in applications_per_month.keys()]
        counts = list(applications_per_month.values())

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(months, counts)
        ax.set_xticklabels(months, rotation=45)
        ax.set_title('Applications per Month')
        ax.set_xlabel('Month')
        ax.set_ylabel('Number of Applications')

        canvas = FigureCanvasTkAgg(fig, master=month_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_company_chart(self, notebook, stats):
        company_frame = ttk.Frame(notebook)
        notebook.add(company_frame, text="Applications per Company")

        applications_per_company = stats['applications_per_company']
        companies = list(applications_per_company.keys())
        counts = list(applications_per_company.values())

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(companies, counts)
        ax.set_title('Applications per Company')
        ax.set_xlabel('Number of Applications')
        ax.set_ylabel('Company')

        canvas = FigureCanvasTkAgg(fig, master=company_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_position_chart(self, notebook, stats):
        position_frame = ttk.Frame(notebook)
        notebook.add(position_frame, text="Applications per Position")

        applications_per_position = stats['applications_per_position']
        positions = list(applications_per_position.keys())
        counts = list(applications_per_position.values())

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(positions, counts)
        ax.set_title('Applications per Position')
        ax.set_xlabel('Number of Applications')
        ax.set_ylabel('Position')

        canvas = FigureCanvasTkAgg(fig, master=position_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_text_stats(self, notebook, stats):
        text_frame = ttk.Frame(notebook)
        notebook.add(text_frame, text="Additional Statistics")

        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        text_widget.insert(tk.END, f"Total Applications: {stats['total_applications']}\n\n")
        text_widget.insert(tk.END, f"Average Applications per Month: {stats['avg_applications_per_month']:.2f}\n\n")
        text_widget.insert(tk.END, f"Most Applied Company: {stats['most_applied_company']}\n\n")
        text_widget.insert(tk.END, f"Most Common Position: {stats['most_common_position']}\n\n")
        text_widget.insert(tk.END, f"Success Rate: {stats['success_rate']:.2f}%\n\n")
        text_widget.insert(tk.END, f"Average Response Time: {stats['avg_response_time']:.2f} days\n\n")

        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
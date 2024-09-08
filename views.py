import tkinter as tk

import fontTools
from ttkbootstrap import Style
import ttkbootstrap as ttk
from database import get_all_applications, create_table
from controllers import add_or_update_application, edit_selected, delete_selected
from utils import get_application_statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ApplicationTracker:
    def __init__(self, master):
        self.master = master
        self.style = Style(theme="solar")  # lumen  journal
        self.master.title("Job Application Tracker")
        self.master.geometry("1200x800")

        create_table()  # Create the SQLite table if it doesn't exist
        self.applications = get_all_applications()
        self.status_colors = {
            "Applied": "secondary",            # A neutral, subdued color that's easy on the eyes
            "Interview Scheduled": "primary",     # A calm, cooler tone
            "Offer Received": "success",       # A positive green tone, already suitable for dark backgrounds
            "Rejected": "danger",              # A clear indication of a negative status
            "Withdrawn": "dark",               # A muted, dark tone to match the overall theme
            "Awaiting Response": "info"
        }

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Application Details", padding="20")
        input_frame.pack(fill=tk.X, pady=(0, 20))

        # Company
        ttk.Label(input_frame, text="Company:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_entry = ttk.Entry(input_frame, width=30)
        self.company_entry.grid(row=0, column=1, pady=5)

        # Position
        ttk.Label(input_frame, text="Position:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.position_entry = ttk.Entry(input_frame, width=30)
        self.position_entry.grid(row=0, column=3, pady=5)

        # Date Applied
        ttk.Label(input_frame, text="Date Applied (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_applied_entry = ttk.Entry(input_frame, width=30)
        self.date_applied_entry.grid(row=1, column=1, pady=5)

        # Status
        ttk.Label(input_frame, text="Status:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.status_combo = ttk.Combobox(input_frame, values=list(self.status_colors.keys()), width=28)
        self.status_combo.grid(row=1, column=3, pady=5)
        self.status_combo.set("Applied")

        # Reminder Date
        ttk.Label(input_frame, text="Reminder Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.reminder_date_entry = ttk.Entry(input_frame, width=90)
        self.reminder_date_entry.grid(row=3, column=1, columnspan=3, pady=5)

        # Notes
        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.notes_entry = ttk.Entry(input_frame, width=90)
        self.notes_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, pady=5)

        # Add/Update Button
        ttk.Button(input_frame, text="Add/Update Application", command=self.add_or_update_application, style='primary.TButton').grid(row=4, column=1, columnspan=2, pady=20)

        # Table Frame
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date"), show="headings", style='info.Treeview')
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
        button_frame = ttk.Frame(main_frame, padding="20")
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Edit Selected", command=self.edit_selected, style='info.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected, style='danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Analytics", command=self.open_analytics_window, style='success.TButton').pack(side=tk.LEFT, padx=5)

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
            self.tree.tag_configure(status, background=self.style.colors.get(color),foreground="black")

        # Configure Treeview style
        style = ttk.Style()
        style.configure('info.Treeview', background='black', foreground='white', fieldbackground='black')
        style.configure('info.Treeview.Heading', background='gray20', foreground='white')

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
        self.style = Style(theme="solar")
        self.master.title("Application Analytics")
        self.master.geometry("800x600")
        self.applications = applications
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.master, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        stats = get_application_statistics()

        notebook = ttk.Notebook(frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 2x2 grid for charts
        charts_frame = ttk.Frame(notebook)
        notebook.add(charts_frame, text="Charts")
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)

        # Status Chart
        status_frame = ttk.Frame(charts_frame)
        status_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.create_status_chart(status_frame, stats)

        # Month Chart
        month_frame = ttk.Frame(charts_frame)
        month_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.create_month_chart(month_frame, stats)

        # Company Chart
        company_frame = ttk.Frame(charts_frame)
        company_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.create_company_chart(company_frame, stats)

        # Position Chart
        position_frame = ttk.Frame(charts_frame)
        position_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.create_position_chart(position_frame, stats)

        # Text widget for additional statistics
        self.create_text_stats(notebook, stats)

    def create_status_chart(self, parent, stats):
        statuses = stats['applications_per_status']
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.pie(statuses.values(), labels=statuses.keys(), autopct='%1.1f%%', startangle=90,textprops={'fontsize': 8})
        ax.axis('equal')
        ax.set_title('Application Statuses', fontsize=10)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_month_chart(self, parent, stats):
        applications_per_month = stats['applications_per_month']
        months = [str(month) for month in applications_per_month.keys()]
        counts = list(applications_per_month.values())

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.bar(months, counts)
        ax.set_xticklabels(months, rotation=45, ha='right', fontsize=8)
        ax.set_title('Applications per Month', fontsize=10)
        ax.set_ylabel('Number of Applications', fontsize=8)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_company_chart(self, parent, stats):
        applications_per_company = stats['applications_per_company']
        companies = list(applications_per_company.keys())[:5]  # Top 5 companies
        counts = list(applications_per_company.values())[:5]

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.barh(companies, counts)
        ax.set_title('Top 5 Companies', fontsize=10)
        ax.set_xlabel('Number of Applications', fontsize=8)
        ax.set_ylabel('Company', fontsize=8)
        ax.tick_params(axis='y', labelsize=8)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_position_chart(self, parent, stats):
        applications_per_position = stats['applications_per_position']
        positions = list(applications_per_position.keys())[:5]  # Top 5 positions
        counts = list(applications_per_position.values())[:5]

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.barh(positions, counts)
        ax.set_title('Top 5 Positions', fontsize=10)
        ax.set_xlabel('Number of Applications', fontsize=8)
        ax.set_ylabel('Position', fontsize=8)
        ax.tick_params(axis='y', labelsize=8)

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_text_stats(self, notebook, stats):
        text_frame = ttk.Frame(notebook, padding="10")
        notebook.add(text_frame, text="Additional Statistics")

        # Create a Text widget with custom colors
        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10, height=20, bg=self.style.colors.get('dark'),
                              fg=self.style.colors.get('light'))
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Add a header
        header = "Additional Statistics\n" + "=" * 30 + "\n\n"

        # Format statistics
        stats_text = (
            f"Total Applications: {stats['total_applications']}\n\n"
            f"Average Applications per Month: {stats['avg_applications_per_month']:.2f}\n\n"
            f"Most Applied Company: {stats['most_applied_company']}\n\n"
            f"Most Common Position: {stats['most_common_position']}\n\n"
            f"Success Rate: {stats['success_rate']:.2f}%\n\n"
            f"Average Response Time: {stats['avg_response_time']:.2f} days\n\n"
        )

        # Insert header and stats into the text widget
        text_widget.insert(tk.END, header + stats_text)
        text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

        # Optional: Add a scrollbar if content exceeds widget height
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)


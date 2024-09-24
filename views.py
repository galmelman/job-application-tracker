import ttkbootstrap as ttk
from database import get_all_applications, create_table, get_application_by_id, update_application, insert_application
from controllers import add_or_update_application, validate_date, delete_selected, check_date
from utils import get_application_statistics, load_settings
from models import JobApplication
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webview
from tkinter import messagebox, ttk
import json
import os
import folium
from folium.plugins import MarkerCluster
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Querybox
from datetime import datetime, timedelta


class ApplicationTracker:
    def __init__(self, master):
        self.master = master
        try:
            self.settings = self.load_settings()
            self.style = Style(theme=self.settings.get("theme", "solar"))
            self.master.title("Job Application Tracker")
            self.master.geometry("1950x1200")

            try:
                create_table()
                self.applications = get_all_applications()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to initialize database , make sure valid data base is "
                                                       f"in project files: {str(e)}")
                self.applications = []

            self.status_colors = {
                "Applied": "secondary",
                "Interview Scheduled": "primary",
                "Offer Received": "success",
                "Rejected": "danger",
                "Withdrawn": "dark",
                "Awaiting Response": "info"
            }
            self.create_widgets()
            self.update_status_colors()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize application: {str(e)}")

    def create_widgets(self):
        try:
            main_frame = ttk.Frame(self.master, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Create left frame for table
            left_frame = ttk.Frame(main_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Table Frame
            table_frame = ttk.Frame(left_frame)
            table_frame.pack(fill=tk.BOTH, expand=True)

            # Configure style for Treeview
            self.style.configure("Treeview", background="black", fieldbackground="black", foreground="white")
            self.style.configure("Treeview.Heading", background="gray20", foreground="white")

            # Treeview
            self.tree = ttk.Treeview(table_frame, columns=("ID", "Company", "Position", "Date Applied", "Status"),
                                     show="headings", style='Treeview')
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Scrollbar
            scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.configure(yscrollcommand=scrollbar.set)

            # Treeview Headings
            for col in ("ID", "Company", "Position", "Date Applied", "Status"):
                self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))
                self.tree.column(col, width=100)

            # Bind double-click event
            self.tree.bind("<Double-1>", self.open_application_details)

            # set map view object
            try:
                self.map_view = MapView(self.master, self.applications)
            except Exception as e:
                messagebox.showwarning("Map View Error", f"Failed to initialize map view: {str(e)}")
                self.map_view = None

            # Buttons Frame
            button_frame = ttk.Frame(left_frame, padding="20")
            button_frame.pack(fill=tk.X)

            ttk.Button(button_frame, text="Add New Application", command=self.open_add_application_window,
                       style='success.TButton').pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected, style='danger.TButton').pack(
                side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Open Map", command=self.open_map,
                       style='info.TButton').pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Settings", command=self.open_settings, style='secondary.TButton').pack(
                side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Help", command=self.open_help_window, style='info.TButton').pack(
                side=tk.LEFT, padx=5)

            # Create right frame for analytics
            right_frame = ttk.Frame(main_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            # Add analytics to right frame
            try:
                self.analytics_view = AnalyticsView(right_frame, self.applications)
            except Exception as e:
                messagebox.showwarning("Analytics Error",
                                       f"Failed to initialize analytics view, make sure valid data base is "
                                       f"in project files: {str(e)}")
                self.analytics_view = None

            self.update_table()
        except Exception as e:
            messagebox.showerror("Widget Creation Error", f"Failed to create widgets: {str(e)}")

    def open_help_window(self):
        try:
            HelpWindow(self.master)
        except Exception as e:
            messagebox.showerror("Help Window Error", f"Failed to open help window: {str(e)}")

    def open_add_application_window(self):
        try:
            AddApplicationWindow(self.master, self.update_table, self.settings)
        except Exception as e:
            messagebox.showerror("Add Application Error", f"Failed to open add application window: {str(e)}")

    def open_application_details(self, event):
        try:
            item = self.tree.selection()[0]
            app_id = self.tree.item(item, "values")[0]
            ApplicationDetailsWindow(self.master, app_id, self.update_table, self.settings)
        except IndexError:
            messagebox.showwarning("Selection Error", "Please select an application to view details.")
        except Exception as e:
            messagebox.showerror("Application Details Error", f"Failed to open application details: {str(e)}")

    def delete_selected(self):
        try:
            delete_selected(self.tree, self.update_table)
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete selected application(s): {str(e)}")

    def update_table(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.applications = get_all_applications()
            for app in self.applications:
                item = self.tree.insert("", "end",
                                        values=(app.id, app.company, app.position, app.date_applied, app.status))
                self.tree.item(item, tags=(app.status,))

            self.update_status_colors()

            if self.analytics_view:
                self.analytics_view.update_analytics(self.applications)

            if self.map_view:
                self.map_view.update_map_data(self.applications)
        except Exception as e:
            messagebox.showerror("Update Table Error", f"Failed to update table: {str(e)}")

    def update_status_colors(self):
        try:
            for status, color in self.status_colors.items():
                bg_color = self.style.lookup(color + '.TButton', 'background')
                fg_color = self.style.lookup(color + '.TButton', 'foreground')
                self.tree.tag_configure(status, background=bg_color, foreground=fg_color)
        except Exception as e:
            messagebox.showwarning("Color Update Error", f"Failed to update status colors: {str(e)}")

    def sort_treeview(self, col, reverse):
        try:
            items = [(self.tree.set(item_id, col), item_id) for item_id in self.tree.get_children('')]
            items.sort(reverse=reverse)
            for index, (value, item_id) in enumerate(items):
                self.tree.move(item_id, '', index)
            self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))
        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort treeview: {str(e)}")

    def refresh_ui(self):
        try:
            self.settings = self.load_settings()
            new_theme = self.settings.get("theme", "solar")
            self.style.theme_use(new_theme)
            self.update_treeview_colors()
            self.update_status_colors()
            self.update_table()
            if self.analytics_view:
                self.analytics_view.update_analytics(self.applications)
        except Exception as e:
            messagebox.showerror("Refresh UI Error", f"Failed to refresh UI: {str(e)}")

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"theme": "solar", "default_status": "Applied"}
        except Exception as e:
            messagebox.showwarning("Settings Error", f"Failed to load settings: {str(e)}")
            return {"theme": "solar", "default_status": "Applied"}

    def update_treeview_colors(self):
        try:
            bg_color = self.style.colors.get('bg')
            fg_color = self.style.colors.get('fg')
            self.style.configure('Treeview', background=bg_color, fieldbackground=bg_color, foreground=fg_color)
            self.style.configure('Treeview.Heading', background=self.style.colors.get('secondary'), foreground=fg_color)
        except Exception as e:
            messagebox.showwarning("Color Update Error", f"Failed to update treeview colors: {str(e)}")

    def update_application(self, app_id, updated_app):
        try:
            update_application(app_id, updated_app)
            self.update_table()
        except Exception as e:
            messagebox.showerror("Update Error", f"Failed to update application: {str(e)}")

    def open_settings(self):
        try:
            SettingsWindow(self.master, self.refresh_ui)
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to open settings window: {str(e)}")

    def open_map(self):
        if self.map_view:
            try:
                self.map_view.open_map_view()
            except Exception as e:
                messagebox.showerror("Map View Error", f"Failed to open map view: {str(e)}")
        else:
            messagebox.showwarning("Map View Unavailable", "Map view is not available.")


class SettingsWindow:
    def __init__(self, master, refresh_callback):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Settings")
        self.window.geometry("400x500")
        self.settings = load_settings()
        self.refresh_callback = refresh_callback
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Theme:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_combo = ttk.Combobox(frame, values=["solar", "darkly", "superhero", "cosmo", "flatly", "litera"],
                                        width=28)
        self.theme_combo.grid(row=0, column=1, pady=5)
        self.theme_combo.set(self.settings.get("theme", "solar"))

        ttk.Label(frame, text="Default Status:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.default_status_combo = ttk.Combobox(frame,
                                                 values=["Applied", "Interview Scheduled", "Offer Received", "Rejected",
                                                         "Withdrawn", "Awaiting Response"], width=28)
        self.default_status_combo.grid(row=1, column=1, pady=5)
        self.default_status_combo.set(self.settings.get("default_status", "Applied"))

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(frame, width=30)
        self.email_entry.grid(row=2, column=1, pady=5)
        self.email_entry.insert(0, self.settings.get("email", ""))

        self.mailing_var = tk.BooleanVar(value=self.settings.get("mailing_enabled", False))
        self.mailing_check = ttk.Checkbutton(frame, text="Enable Mailing", variable=self.mailing_var)
        self.mailing_check.grid(row=3, column=0, columnspan=2, pady=5)

        ttk.Button(frame, text="Save Settings", command=self.save_settings).grid(row=4, column=0, columnspan=2, pady=20)

    def save_settings(self):
        settings = {
            "theme": self.theme_combo.get(),
            "default_status": self.default_status_combo.get(),
            "email": self.email_entry.get(),
            "mailing_enabled": self.mailing_var.get()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.window.destroy()
        self.refresh_callback()


class HelpWindow:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Job Application Tracker - Help")
        self.window.geometry("600x400")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(frame, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)

        help_text = """
        Welcome to the Job Application Tracker!

        Here's how to use the application:

        1. Adding a New Application:
           - Click the "Add New Application" button.
           - Fill in the required details and click "Add Application".

        2. Viewing Applications:
           - All your applications are displayed in the main table.
           - Double-click on an application to view or edit its details.

        3. Editing an Application:
           - Double-click on an application in the table.
           - Update the information in the new window and click "Update Application".

        4. Deleting an Application:
           - Select an application in the table.
           - Click the "Delete Selected" button.

        5. Using the Map View:
           - Click the "Open Map" button to see the geographical distribution of your applications.

        6. Viewing Analytics:
           - The right side of the main window shows various charts and statistics about your applications.

        7. Changing Settings:
           - Click the "Settings" button to customize the application theme and other options.

        8. Reminders:
           - The application will show reminders for follow-ups based on the reminder date you set for each application.

        Remember to keep your application information up-to-date for the best experience!
        """

        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)  # Make the text widget read-only

        ttk.Button(frame, text="Close", command=self.window.destroy).pack(pady=10)


class AddApplicationWindow:
    def __init__(self, master, update_callback, settings):
        self.window = tk.Toplevel(master)
        self.window.title("Add New Application")
        self.window.geometry("500x600")
        self.update_callback = update_callback
        self.settings = settings
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Company:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_entry = ttk.Entry(frame, width=30)
        self.company_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Position:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.position_entry = ttk.Entry(frame, width=30)
        self.position_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Date Applied:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_applied_picker = DateEntry(frame)
        self.date_applied_picker.grid(row=2, column=1, pady=5)
        self.date_applied_picker.set(datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(frame, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_combo = ttk.Combobox(frame, values=["Applied", "Interview Scheduled", "Offer Received", "Rejected",
                                                        "Withdrawn", "Awaiting Response"], width=28)
        self.status_combo.grid(row=3, column=1, pady=5)
        self.status_combo.set(self.settings.get("default_status", "Applied"))

        ttk.Label(frame, text="Location (Full Address):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.location_entry = ttk.Entry(frame, width=30)
        self.location_entry.grid(row=4, column=1, pady=5)

        ttk.Label(frame, text="Reminder Date:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.reminder_date_picker = DateEntry(frame)
        self.reminder_date_picker.grid(row=5, column=1, pady=5)
        self.reminder_date_picker.set((datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"))

        ttk.Button(frame, text="Add Application", command=self.add_application, style='success.TButton').grid(row=6,
                                                                                                              column=0,
                                                                                                              columnspan=2,
                                                                                                              pady=20)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"theme": "solar", "default_status": "Applied", "email": "", "mailing_enabled": False}

    def add_application(self):
        company = self.company_entry.get().strip()
        position = self.position_entry.get().strip()
        date_applied = self.date_applied_picker.get()
        reminder_date = self.reminder_date_picker.get()
        status = self.status_combo.get()
        location = self.location_entry.get().strip()

        if not company or not position or not location:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        new_app = JobApplication(company, position, date_applied, status, location=location,
                                 reminder_date=reminder_date)
        add_or_update_application(self)
        self.window.destroy()


class ApplicationDetailsWindow:
    def __init__(self, master, app_id, update_callback, settings):
        self.window = tk.Toplevel(master)
        self.window.title("Application Details")
        self.window.geometry("1000x1000")
        self.app_id = app_id
        self.update_callback = update_callback
        self.settings = settings
        self.app = get_application_by_id(app_id)
        self.create_widgets()

    def create_widgets(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True)

        details_frame = ttk.Frame(notebook, padding="20")
        notebook.add(details_frame, text="Details")

        roadmap_frame = ttk.Frame(notebook, padding="20")
        notebook.add(roadmap_frame, text="Roadmap")

        self.create_details_widgets(details_frame)
        self.create_roadmap_widgets(roadmap_frame)

    def create_details_widgets(self, parent):
        ttk.Label(parent, text="Company:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.company_entry = ttk.Entry(parent, width=30)
        self.company_entry.grid(row=0, column=1, pady=5)
        self.company_entry.insert(0, self.app.company)

        ttk.Label(parent, text="Position:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.position_entry = ttk.Entry(parent, width=30)
        self.position_entry.grid(row=1, column=1, pady=5)
        self.position_entry.insert(0, self.app.position)

        ttk.Label(parent, text="Date Applied:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.date_applied_picker = DateEntry(parent)
        self.date_applied_picker.grid(row=2, column=1, pady=5)
        self.date_applied_picker.set(self.app.date_applied)

        ttk.Label(parent, text="Status:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.status_combo = ttk.Combobox(parent, values=["Applied", "Interview Scheduled", "Offer Received", "Rejected",
                                                         "Withdrawn", "Awaiting Response"], width=28)
        self.status_combo.grid(row=3, column=1, pady=5)
        self.status_combo.set(self.app.status)

        ttk.Label(parent, text="Notes:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.notes_entry = ttk.Entry(parent, width=50)
        self.notes_entry.grid(row=4, column=1, columnspan=2, pady=5)
        self.notes_entry.insert(0, self.app.notes)

        ttk.Label(parent, text="Location:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.location_entry = ttk.Entry(parent, width=30)
        self.location_entry.grid(row=5, column=1, pady=5)
        self.location_entry.insert(0, self.app.location)

        ttk.Label(parent, text="Salary Offered:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.salary_entry = ttk.Entry(parent, width=30)
        self.salary_entry.grid(row=6, column=1, pady=5)
        self.salary_entry.insert(0, str(self.app.salary_offered) if self.app.salary_offered else "")

        ttk.Label(parent, text="Job Description:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.job_description_entry = ttk.Entry(parent, width=50)
        self.job_description_entry.grid(row=7, column=1, columnspan=2, pady=5)
        self.job_description_entry.insert(0, self.app.job_description)

        ttk.Label(parent, text="Company Culture:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.company_culture_entry = ttk.Entry(parent, width=50)
        self.company_culture_entry.grid(row=8, column=1, columnspan=2, pady=5)
        self.company_culture_entry.insert(0, self.app.company_culture)

        ttk.Label(parent, text="Interviewer Names:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.interviewer_names_entry = ttk.Entry(parent, width=50)
        self.interviewer_names_entry.grid(row=9, column=1, columnspan=2, pady=5)
        self.interviewer_names_entry.insert(0, self.app.interviewer_names)

        ttk.Label(parent, text="Reminder Date:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.reminder_date_picker = DateEntry(parent)
        self.reminder_date_picker.grid(row=10, column=1, pady=5)
        self.reminder_date_picker.set(self.app.reminder_date if self.app.reminder_date else "")

        ttk.Button(parent, text="Update Application", command=self.update_application, style='success.TButton').grid(
            row=11, column=0, columnspan=2, pady=20)

    def create_roadmap_widgets(self, parent):
        stages = [
            ("Application Submitted", self.app.application_submitted),
            ("Resume Screened", self.app.resume_screened),
            ("Phone Interview", self.app.phone_interview),
            ("Technical Interview", self.app.technical_interview),
            ("Onsite Interview", self.app.onsite_interview),
            ("Offer Received", self.app.offer_received),
            ("Offer Accepted", self.app.offer_accepted),
            ("Offer Rejected", self.app.offer_rejected)
        ]

        # Create a frame for displaying the roadmap
        display_frame = ttk.Frame(parent)
        display_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Create a frame for editing the roadmap
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Display roadmap
        ttk.Label(display_frame, text="Application Roadmap", font=("", 14, "bold")).pack(pady=10)
        for stage, date in stages:
            frame = ttk.Frame(display_frame, borderwidth=1, relief="raised", padding=10)
            frame.pack(fill=tk.X, padx=5, pady=5)
            ttk.Label(frame, text=stage, font=("", 12, "bold")).pack(side=tk.LEFT, padx=5)
            ttk.Label(frame, text=date if date else "Not yet").pack(side=tk.RIGHT, padx=5)

        # Edit roadmap
        self.roadmap_entries = {}
        for stage, date in stages:
            frame = ttk.Frame(edit_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=stage + ":").pack(side=tk.LEFT, padx=5)
            date_picker = DateEntry(frame)
            date_picker.pack(side=tk.RIGHT, padx=5)

            # Bind the validation function to the date entry widget
            date_picker.bind("<FocusOut>", check_date)

            if date:
                date_picker.set(date)
            self.roadmap_entries[stage] = date_picker

        ttk.Button(edit_frame, text="Update Roadmap", command=self.update_roadmap, style='info.TButton').pack(pady=20)

    def update_roadmap(self):
        self.app.application_submitted = self.roadmap_entries["Application Submitted"].get()
        self.app.resume_screened = self.roadmap_entries["Resume Screened"].get()
        self.app.phone_interview = self.roadmap_entries["Phone Interview"].get()
        self.app.technical_interview = self.roadmap_entries["Technical Interview"].get()
        self.app.onsite_interview = self.roadmap_entries["Onsite Interview"].get()
        self.app.offer_received = self.roadmap_entries["Offer Received"].get()
        self.app.offer_accepted = self.roadmap_entries["Offer Accepted"].get()
        self.app.offer_rejected = self.roadmap_entries["Offer Rejected"].get()

        update_application(self.app_id, self.app)
        self.update_callback()
        messagebox.showinfo("Success", "Roadmap updated successfully.")

    def update_application(self):
        self.app.company = self.company_entry.get().strip()
        self.app.position = self.position_entry.get().strip()
        self.app.date_applied = self.date_applied_picker.get()
        self.app.reminder_date = self.reminder_date_picker.get()
        self.app.status = self.status_combo.get()
        self.app.notes = self.notes_entry.get().strip()
        self.app.location = self.location_entry.get().strip()
        self.app.salary_offered = float(self.salary_entry.get().strip()) if self.salary_entry.get().strip() else None
        self.app.job_description = self.job_description_entry.get().strip()
        self.app.company_culture = self.company_culture_entry.get().strip()
        self.app.interviewer_names = self.interviewer_names_entry.get().strip()

        add_or_update_application(self)
        self.update_callback()
        messagebox.showinfo("Success", "Application updated successfully.")


class MapView:
    def __init__(self, master, applications):
        self.master = master
        self.applications = applications
        self.geolocator = Nominatim(user_agent="job_application_tracker")
        self.cached_locations = {}  # Cache to store geocoded locations

    def open_map_view(self):
        # Create a window to display the map

        m = folium.Map(location=[31.0461, 34.8516],
                       zoom_start=8)  # Latitude and Longitude for Israel, feel free to change it

        # Add markers for each application location
        marker_cluster = MarkerCluster().add_to(m)

        # Iterate over applications and add markers for valid locations
        for app in self.applications:
            if app.location and app.status != "Rejected":
                location = self.get_cached_location(app.location)
                if location:
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"{app.company} - {app.position}",
                        tooltip=app.location
                    ).add_to(marker_cluster)

        # Save the map to an HTML file
        map_file = "job_locations_map.html"
        m.save(map_file)

        # Use PyWebview to display the HTML map in a window
        webview.create_window("Map", 'file://' + os.path.realpath(map_file))
        webview.start()

        # Clean up by removing the HTML file after the window closes
        os.remove(map_file)

        # Clean the cache of invalid or outdated locations
        self.clean_cache()

    def update_map_data(self, new_applications):
        self.applications = new_applications  # Update the applications list with the new data

        # Regenerate the cached locations based on the updated applications
        for app in self.applications:
            if app.location and app.status != "Rejected":
                if app.location not in self.cached_locations:
                    self.get_cached_location(app.location)

        # Clean up invalid or outdated cached locations
        self.clean_cache()

    def get_cached_location(self, location_name):
        if location_name in self.cached_locations:
            return self.cached_locations[location_name]

        try:
            location = self.geolocator.geocode(location_name)
            if location:
                self.cached_locations[location_name] = location  # Cache the result
                return location
        except (GeocoderTimedOut, GeocoderUnavailable):
            print(f"Geocoding failed for location: {location_name}")
        return None

    def clean_cache(self):

        valid_locations = {app.location for app in self.applications if app.location and app.status != "Rejected"}

        # Remove cached locations that are no longer valid
        locations_to_remove = [loc for loc in self.cached_locations if loc not in valid_locations]

        for loc in locations_to_remove:
            del self.cached_locations[loc]

        print(f"Cache cleaned: {len(locations_to_remove)} locations removed.")


class DateEntry(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.entry = ttk.Entry(self, width=12)
        self.entry.pack(side=tk.LEFT, padx=(0, 5))
        self.button = ttk.Button(self, text="Date", width=3, command=self.show_date_picker)
        self.button.pack(side=tk.LEFT)

    def show_date_picker(self):
        current_date = self.entry.get() or datetime.now().strftime('%Y-%m-%d')
        date = Querybox.get_date(title="Select Date")
        if date:
            self.entry.delete(0, tk.END)
            self.entry.insert(0, date.strftime('%Y-%m-%d'))

    def get(self):
        return self.entry.get()

    def set(self, date):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, date)


class AnalyticsView:
    def __init__(self, master, applications):
        self.master = master
        self.style = Style(theme="solar")
        self.applications = applications
        self.charts_frame = None
        self.text_widget = None
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.master, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Charts tab
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="Charts")
        self.charts_frame.columnconfigure(0, weight=1)
        self.charts_frame.columnconfigure(1, weight=1)
        self.charts_frame.rowconfigure(0, weight=1)
        self.charts_frame.rowconfigure(1, weight=1)

        # Text stats tab
        self.text_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.text_frame, text="Additional Statistics")

        self.text_widget = tk.Text(self.text_frame, wrap=tk.WORD, padx=10, pady=10, height=20,
                                   bg=self.style.colors.get('bg'), fg='white')  # Change text color to white
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        self.update_analytics(self.applications)

    def update_analytics(self, applications):
        self.applications = applications
        stats = get_application_statistics()

        # Clear existing charts
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # Recreate charts
        self.create_status_chart(self.charts_frame, stats)
        self.create_month_chart(self.charts_frame, stats)
        self.create_company_chart(self.charts_frame, stats)
        self.create_position_chart(self.charts_frame, stats)

        # Update text statistics
        self.update_text_stats(stats)

    def create_chart(self, parent, chart_func, row, col):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        try:
            chart_func(frame)
        except Exception as e:
            ttk.Label(frame, text=f"Not enough data to create chart.\nError: {str(e)}", foreground='white').pack(
                expand=True)

    def create_status_chart(self, parent, stats):
        def chart(frame):
            statuses = stats['applications_per_status']
            fig, ax = plt.subplots(figsize=(6, 4), dpi=100, facecolor=self.style.colors.get('bg'))
            colors = [self.style.colors.get(color) for color in ['primary', 'info', 'success', 'danger', 'warning']]
            wedges, texts, autotexts = ax.pie(statuses.values(), labels=statuses.keys(), autopct='%1.1f%%',
                                              startangle=90, colors=colors)
            ax.axis('equal')
            ax.set_title('Application Statuses', color='white')
            plt.setp(texts, color="white")  # Set label color to white
            plt.setp(autotexts, color="white")  # Set percentage text color to white
            self.embed_chart(frame, fig)

        self.create_chart(parent, chart, 0, 0)

    def create_month_chart(self, parent, stats):
        def chart(frame):
            applications_per_month = stats['applications_per_month']
            months = [str(month) for month in applications_per_month.keys()]
            counts = list(applications_per_month.values())

            fig, ax = plt.subplots(figsize=(6, 4), dpi=90, facecolor=self.style.colors.get('bg'))

            # Create the bar chart
            ax.bar(months, counts, color=self.style.colors.get('primary'))

            # Set the ticks and tick labels
            ax.set_xticks(range(len(months)))
            ax.set_xticklabels(months, rotation=45, ha='right')

            # Set title and labels with white color
            ax.set_title('Applications per Month', color='white')
            ax.set_ylabel('Number of Applications', color='white')

            # Set the color for the tick labels to white
            plt.setp(ax.get_yticklabels(), color='white')
            plt.setp(ax.get_xticklabels(), color='white')

            plt.tight_layout()
            self.embed_chart(frame, fig)

        self.create_chart(parent, chart, 0, 1)

    def create_company_chart(self, parent, stats):
        def chart(frame):
            applications_per_company = stats['applications_per_company']
            companies = list(applications_per_company.keys())[:5]  # Top 5 companies
            counts = list(applications_per_company.values())[:5]

            fig, ax = plt.subplots(figsize=(6, 4), dpi=80, facecolor=self.style.colors.get('bg'))
            ax.barh(companies, counts, color=self.style.colors.get('info'))
            ax.set_title('Top 5 Companies', color='white')
            ax.set_xlabel('Number of Applications', color='white')
            ax.set_ylabel('Company', color='white')
            plt.setp(ax.get_yticklabels(), color='white')
            plt.setp(ax.get_xticklabels(), color='white')
            plt.tight_layout()
            self.embed_chart(frame, fig)

        self.create_chart(parent, chart, 1, 0)

    def create_position_chart(self, parent, stats):
        def chart(frame):
            applications_per_position = stats['applications_per_position']
            positions = list(applications_per_position.keys())[:5]  # Top 5 positions
            counts = list(applications_per_position.values())[:5]

            fig, ax = plt.subplots(figsize=(6, 4), dpi=85, facecolor=self.style.colors.get('bg'))
            ax.barh(positions, counts, color=self.style.colors.get('success'))
            ax.set_title('Top 5 Positions', color='white')
            ax.set_xlabel('Number of Applications', color='white')
            ax.set_ylabel('Position', color='white')
            plt.setp(ax.get_yticklabels(), color='white')
            plt.setp(ax.get_xticklabels(), color='white')

            # Adjust layout to show full position names
            plt.tight_layout()
            fig.subplots_adjust(left=0.3)  # Increase left margin to accommodate longer labels

            self.embed_chart(frame, fig)

        self.create_chart(parent, chart, 1, 1)

    def embed_chart(self, parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_text_stats(self, stats):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)

        header = "Additional Statistics\n" + "=" * 30 + "\n\n"
        stats_text = (
            f"Total Applications: {stats['total_applications']}\n\n"
            f"Average Applications per Month: {stats['avg_applications_per_month']:.2f}\n\n"
            f"Most Applied Company: {stats['most_applied_company']}\n\n"
            f"Most Common Position: {stats['most_common_position']}\n\n"
            f"Success Rate: {stats['success_rate']:.2f}%\n\n"
            f"Average Response Time: {stats['avg_response_time']:.2f} days\n\n"
        )

        self.text_widget.insert(tk.END, header + stats_text)
        self.text_widget.config(state=tk.DISABLED)  # Make the text widget read-only

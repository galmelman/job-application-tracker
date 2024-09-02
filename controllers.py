import tkinter as tk
from tkinter import messagebox
from models import JobApplication


def add_or_update_application(applications, tree, company_entry, position_entry, date_applied_entry, status_combo,
                              notes_entry,reminder_date_entry, save_applications, update_table, clear_entries):
    company = company_entry.get().strip()
    position = position_entry.get().strip()
    date_applied = date_applied_entry.get().strip()
    status = status_combo.get()
    notes = notes_entry.get().strip()
    reminder_date = reminder_date_entry.get().strip()

    if not company or not position:
        messagebox.showwarning("Input Error", "Company and Position are required fields.")
        return

    if not validate_date(date_applied):
        messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
        return

    selected_items = tree.selection()
    if selected_items:
        # Update existing application
        item = selected_items[0]
        index = tree.index(item)
        applications[index] = JobApplication(company, position, date_applied, status, notes, reminder_date)
    else:
        # Add new application
        new_app = JobApplication(company, position, date_applied, status, notes, reminder_date)
        applications.append(new_app)

    save_applications()
    update_table()
    clear_entries()


def edit_selected(tree, company_entry, position_entry, date_applied_entry, status_combo, notes_entry, reminder_date_entry):
    selected_items = tree.selection()
    if selected_items:
        item = selected_items[0]
        values = tree.item(item)['values']
        company_entry.delete(0, tk.END)
        company_entry.insert(0, values[0])
        position_entry.delete(0, tk.END)
        position_entry.insert(0, values[1])
        date_applied_entry.delete(0, tk.END)
        date_applied_entry.insert(0, values[2])
        status_combo.set(values[3])
        notes_entry.delete(0, tk.END)
        notes_entry.insert(0, values[4])
        reminder_date_entry.delete(0, tk.END)
        reminder_date_entry.insert(0, values[5])
    else:
        messagebox.showinfo("Selection", "Please select an application to edit.")

def delete_selected(tree, applications, save_applications, update_table):
    selected_items = tree.selection()
    if selected_items:
        if messagebox.askyesno("Delete", "Are you sure you want to delete the selected application?"):
            item = selected_items[0]
            index = tree.index(item)
            del applications[index]
            save_applications()
            update_table()
    else:
        messagebox.showinfo("Selection", "Please select an application to delete.")

def validate_date(date_string):
    import re
    from datetime import datetime
    if not date_string:
        return True  # Allow empty date
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not pattern.match(date_string):
        return False
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

import ttkbootstrap as ttk
from views import ApplicationTracker
from utils import setup_reminder_check

if __name__ == "__main__":

    root = ttk.Window(themename="solar")
    app = ApplicationTracker(root)

    setup_reminder_check(root, app.applications, app.settings)

    root.mainloop()



import tkinter as tk
from views import ApplicationTracker,create_analytics_frame
from utils import setup_reminder_check

if __name__ == "__main__":
    root = tk.Tk()
    app = ApplicationTracker(root)

    # Start the reminder check process
    setup_reminder_check(root, app.applications)

    # Add Analytics Frame
    analytics_frame = create_analytics_frame(root, app.applications)

    root.mainloop()

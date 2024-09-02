# Job Application Tracker

A Python application using Tkinter for tracking job applications. This tool allows users to manage their job search process by recording details about job applications, including company name, position, application date, status, and notes. It now includes a feature to set reminders for follow-up actions.

## Features

- **Add/Update Applications**: Enter and update details about job applications.
- **Edit Applications**: Modify details of selected job applications.
- **Delete Applications**: Remove job applications from the list.
- **View Applications**: Display a list of all job applications with their details.
- **Reminder Feature**: Set reminders for follow-up actions on job applications. The application will notify you if you need to follow up with a company based on the reminder date.

## Files

- `main.py`: Initializes the application and starts the Tkinter event loop.
- `views.py`: Contains the Tkinter UI components and layout.
- `controllers.py`: Contains the logic for managing job applications.
- `utils.py`: Includes utility functions for handling reminders and data operations.

## Installation

Ensure you have Python installed. Clone this repository and run the following command to install the required packages:

```bash
pip install -r requirements.txt

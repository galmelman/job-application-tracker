# Job Application Tracker

## Overview

The Job Application Tracker is a desktop application built using Tkinter that helps users track their job applications. It provides features to add, update, delete, and visualize job application data.

## Features

- **Add/Update/Delete Applications**: Easily manage your job applications with a simple user interface.
- **Reminder Feature**: Set reminders for follow-up actions on your applications.
- **Real-Time Analytics and Visualization**: 
  - The application automatically visualizes the status of your applications with a pie chart.
  - A bar chart displays the number of applications submitted each month.
  - Detailed statistics such as total applications, applications per status, company, position, and month are generated and displayed.
- **CSV Integration**: Save and load your application data from a CSV file.

## Installation

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies by running:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    python main.py
    ```

## Dependencies

- Tkinter: For the graphical user interface.
- ttkthemes: For additional themes.
- Matplotlib: For generating visualizations.
- Pandas: For data manipulation and generating statistics.
- CSV: For saving and loading application data.
- Datetime: For handling date-related operations.
- Re: For regular expressions.

## How to Use

1. **Adding a New Application**: Enter the details of your job application, including the company name, position, date applied, status, and any notes or reminders. Click the "Add Application" button to save the entry.

2. **Editing an Application**: Select an application from the list, make your changes, and click "Edit Selected" to update the entry.

3. **Deleting an Application**: Select an application from the

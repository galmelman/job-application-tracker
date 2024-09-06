# Job Application Tracker

## Overview

The Job Application Tracker is a desktop application built using Tkinter that helps users track their job applications. It provides features to add, update, delete, and visualize job application data, with SQLite database integration for efficient data management.

## Features

- **Add/Update/Delete Applications**: Easily manage your job applications with a simple user interface.
- **Reminder Feature**: Set reminders for follow-up actions on your applications.
- **Real-Time Analytics and Visualization**: 
  - The application automatically visualizes the status of your applications with a pie chart.
  - A bar chart displays the number of applications submitted each month.
  - Detailed statistics such as total applications, applications per status, company, position, and month are generated and displayed.
- **SQLite Database**: Efficient and reliable storage of application data using SQLite.
- **Data Persistence**: Your application data is automatically saved and loaded from the SQLite database.

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
- SQLite3: For database operations.
- Matplotlib: For generating visualizations.
- Pandas: For data manipulation and generating statistics.
- Datetime: For handling date-related operations.

## How to Use

1. **Adding a New Application**: Enter the details of your job application, including the company name, position, date applied, status, notes, and reminder date. Click the "Add/Update Application" button to save the entry.

2. **Editing an Application**: Select an application from the list, make your changes in the input fields, and click "Add/Update Application" to update the entry.

3. **Deleting an Application**: Select an application from the list and click "Delete Selected" to remove the entry.

4. **Viewing Statistics**: The application automatically generates and displays statistics about your job applications, including pie charts for application statuses and bar charts for applications per month.

5. **Setting Reminders**: Enter a reminder date for an application, and the system will notify you when it's time to follow up.

## Project Structure

- `main.py`: The entry point of the application.
- `views.py`: Contains the main GUI implementation.
- `controllers.py`: Handles the logic for adding, updating, and deleting applications.
- `models.py`: Defines the JobApplication class.
- `database.py`: Manages SQLite database operations.
- `utils.py`: Contains utility functions for reminders and statistics.

## Contributing

Contributions to improve the Job Application Tracker are welcome. Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

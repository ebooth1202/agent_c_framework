# Time Log Update Instructions

## Automatic Update Process

Whenever time is logged to an issue or project, follow these steps to ensure the master time log stays in sync:

### 1. Determine the correct weekly log file

Time entries should be added to the weekly log that contains the date of the work.
- Format: `YYYY-MM-DD_weekly_log.md` (where the date is the Monday of that week)
- Example: `2025-10-06_weekly_log.md` for any work done between Oct 6-10, 2025

### 2. Add the new time entry to the weekly log

Add a new row to the time entries table with:
- Date: The date the work was performed
- Hours: Number of hours worked
- Client: Client name or "Internal" for internal projects
- Project/Issue: Name of the project or issue identifier
- Description: Brief description of the work performed

### 3. Update the summary section

- Recalculate the total hours
- Update the project breakdown with new totals

## Creating a New Weekly Log

At the start of each week (Monday):

1. Copy the `time_log_template.md` file
2. Rename it to `YYYY-MM-DD_weekly_log.md` using the current Monday's date
3. Update the date range in the header
4. Initialize with any scheduled or recurring time entries

## Script Integration

A future enhancement will be to create scripts to automate this synchronization process, ensuring all time entries are always reflected in both the issue trackers and the master time log.
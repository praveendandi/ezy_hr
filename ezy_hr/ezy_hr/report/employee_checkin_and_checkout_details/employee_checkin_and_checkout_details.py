# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt

# import frappe


import frappe
from frappe.utils import getdate, time_diff, time_diff_in_hours
from datetime import timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 180},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 180},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 150},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Duration", "fieldname": "working_hours", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 180},
        {"label": "Actions", "fieldname": "actions", "fieldtype": "Button", "width": 180}
    ]

def get_data(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append(["Employee Checkin", "time", ">=", filters['from_date'] + ' 00:00:00'])
    if filters.get("to_date"):
        conditions.append(["Employee Checkin", "time", "<=", filters['to_date'] + ' 23:59:59'])
    if filters.get("employee"):
        conditions.append(["Employee Checkin", "employee", "=", filters['employee']])
    if filters.get("company"):
        conditions.append(["Employee", "company", "=", filters['company']])

    # Generate date range
    date_range = get_date_range(filters['from_date'], filters['to_date'])
    
    employees = frappe.get_all('Employee', filters={'status': 'Active', 'company': filters['company']}, fields=['name', 'employee_name', 'company', 'department', 'designation', 'date_of_joining'])

    data = []
    leave_details = get_leave_dates(filters)

    for emp in employees:
        for date in date_range:
            checkins = frappe.get_all('Employee Checkin', filters=[
                ['employee', '=', emp['name']],
                ['time', 'between', [date + ' 00:00:00', date + ' 23:59:59']]
            ], fields=['time', 'log_type'])

            in_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'IN'), None)
            out_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'OUT'), None)
            working_hours = calculate_working_hours(in_time, out_time)
            status = determine_status(in_time, out_time, leave_details, emp['name'], date)

            data.append({
                'employee': emp['name'],
                'employee_name': emp['employee_name'],
                'department': emp['department'],
                'designation': emp['designation'],
                'date_of_joining': emp['date_of_joining'],
                'date': date,
                'in_time': in_time,
                'out_time': out_time,
                'working_hours': working_hours,
                'status': status,
                'actions': generate_actions(status, emp['name'], date)
            })
    
    if not filters.get("include_all"):
        data = [row for row in data if row["status"] != ["P"]]

    # Filter data based on the employee filter
    if filters.get("employee"):
        data = [row for row in data if row["employee"] == filters["employee"]]

    return data

def get_date_range(start_date, end_date):
    start = getdate(start_date)
    end = getdate(end_date)
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def calculate_working_hours(in_time, out_time):
    if in_time and out_time:
        duration = time_diff(out_time, in_time)
        hours = time_diff_in_hours(out_time, in_time)
        return f"{int(hours):02}:{int(duration.total_seconds() / 60 % 60):02}"
    return None

def determine_status(in_time, out_time, leave_details, employee, date):
    if employee in leave_details and date in leave_details[employee]:
        return leave_details[employee][date]
    if not in_time and not out_time:
        return 'Missing Punches'
    if not in_time:
        return 'MI'
    if not out_time:
        return 'MO'
    return 'P'

def generate_actions(status, employee, date):
    if status == "Missing Punches":
        return f'<a href="#" onclick="openPopup(\'{employee}\', \'{date}\')">Click to Add Attendance</a>'
    elif status == "MI":
        return f'<a href="#" onclick="openPopupforcheckin(\'{employee}\', \'{date}\')">Add Checkin</a>'
    elif status == "MO":
        return f'<a href="#" onclick="openPopupforcheckout(\'{employee}\', \'{date}\')">Add Checkout</a>'
    return ''


def get_leave_dates(filters):
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    if not start_date or not end_date:
        return {}

    leave_data = frappe.get_all("Attendance", filters={"attendance_date": ["between", [start_date, end_date]]}, fields=["employee", "attendance_date", "status", "leave_type"])
    print(leave_data,"////////////////")
    leave_details = {}
    for entry in leave_data:
        date = getdate(entry["attendance_date"]).strftime("%Y-%m-%d")
        leave_type = entry.get("status")
        employee = entry["employee"]
        if employee not in leave_details:
            leave_details[employee] = {}
        leave_details[employee][date] = f"{leave_type}" if leave_type else "On Leave"
    
    return leave_details

       

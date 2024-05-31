# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, time_diff_in_seconds
from datetime import timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Duration", "fieldname": "working_hours", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 180},
        {"label": "Actions", "fieldname": "actions", "fieldtype": "Button", "width": 180},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 180},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 180},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 150},
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "hidden": 1, "width": 150},
    ]

def get_data(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append(["time", ">=", filters['from_date'] + ' 00:00:00'])
    if filters.get("to_date"):
        conditions.append(["time", "<=", filters['to_date'] + ' 23:59:59'])
    if filters.get("company"):
        conditions.append(["company", "=", filters['company']])

    date_range = get_date_range(filters['from_date'], filters['to_date'])

    employee_filters = {'status': 'Active', 'company': filters['company']}
    if filters.get("employee"):
        employee_filters['name'] = filters['employee']
    if filters.get("department"):
        employee_filters['department'] = filters['department']

    employees = frappe.get_all('Employee', filters=employee_filters, fields=['name', 'employee_name', 'company', 'department', 'designation', 'date_of_joining', 'holiday_list'])

    data = []
    leave_details = get_leave_dates(filters)
    holiday_details = get_holiday_dates(filters, employees)

    for emp in employees:
        for date in date_range:
            checkins = frappe.get_all('Employee Checkin', filters=[
                ['employee', '=', emp['name']],
                ['time', 'between', [date + ' 00:00:00', date + ' 23:59:59']]
            ], fields=['time', 'log_type'])

            in_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'IN'), None)
            out_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'OUT'), None)
            working_hours = calculate_working_hours(in_time, out_time)
            status = determine_status(in_time, out_time, leave_details, holiday_details, emp['name'], date)

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

    return data

def get_date_range(start_date, end_date):
    print('////////////////////////////////////')
    start = getdate(start_date)
    end = getdate(end_date)
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]

def calculate_working_hours(in_time, out_time):
    if in_time and out_time:
        duration_in_seconds = time_diff_in_seconds(out_time, in_time)
        if duration_in_seconds < 0:
            duration_in_seconds += 24 * 3600
        hours, remainder = divmod(duration_in_seconds, 3600)
        minutes = remainder // 60
        return f"{int(hours):02}:{int(minutes):02}"
    return None

def determine_status(in_time, out_time, leave_details, holiday_details, employee, date):
    if employee in leave_details and date in leave_details[employee]:
        return leave_details[employee][date]

    if employee in holiday_details and date in holiday_details[employee]:
        return holiday_details[employee][date]
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
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    if not start_date or not end_date:
        return {}

    leave_data = frappe.get_all("Attendance", filters={"attendance_date": ["between", [start_date, end_date]]}, fields=["employee", "attendance_date", "status", "leave_type"])
    
    leave_details = {}
    for entry in leave_data:
        date = getdate(entry["attendance_date"]).strftime("%Y-%m-%d")
        leave_type = entry.get("status")
        employee = entry["employee"]
        if employee not in leave_details:
            leave_details[employee] = {}
        leave_details[employee][date] = f"{leave_type}" if leave_type else "On Leave"
    
    return leave_details

def get_holiday_dates(filters, employees):
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    if not start_date or not end_date:
        return {}

    holiday_details = {}
    for emp in employees:
        holiday_list_name = emp.get("holiday_list")
        if not holiday_list_name:
            continue
        holidays = frappe.get_all("Holiday", filters={"holiday_date": ["between", [start_date, end_date]], "parent": holiday_list_name}, fields=["holiday_date", "description"])
        for holiday in holidays:
            date = getdate(holiday["holiday_date"]).strftime("%Y-%m-%d")
            if emp["name"] not in holiday_details:
                holiday_details[emp["name"]] = {}
            holiday_details[emp["name"]][date] = holiday["description"] or "Holiday"
    
    return holiday_details





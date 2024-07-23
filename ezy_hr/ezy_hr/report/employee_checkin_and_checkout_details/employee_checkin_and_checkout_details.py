# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt

import frappe
from frappe.utils import getdate, time_diff_in_seconds
from datetime import timedelta, datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 100},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 110},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 110},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Datetime", "width": 160},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Datetime", "width": 160},
        {"label": "Duration", "fieldname": "working_hours", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
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

    employee_filters = {'status': ['IN',['Left','Active']], 'company': filters['company']}
    if filters.get("employee"):
        employee_filters['name'] = filters['employee']
    if filters.get("department"):
        employee_filters['department'] = filters['department']

    employees = frappe.get_all('Employee', filters=employee_filters, fields=['name', 'employee_name', 'company', 'department', 'designation', 'date_of_joining','relieving_date','holiday_list'])

    data = []
    leave_details = get_leave_dates(filters)
    holiday_details = get_holiday_dates(filters, employees)
    leave_type_short_forms = {
		"Week Off": "WO",
		"Casual Leave": "CL",
		"Sick Leave": "SL",
		"Privilege Leave": "PL",
		"Maternity Leave": "ML",
		"Compensatory Off (COL)": "COL",
		"Compensatory Off": "CO",
		"Accident Leave on shift": "ALS",
		"Leave Without Pay": "LWP",
		"ESI Leave": "ESIL",
		"Holiday": "HO",
		"Unpaid Leave": "UNL",
		"Flexi Week Off":"FWO",
		"Flexi Public Holiday":"FPH",
		"PH Holiday":"PH Holiday",
        "Flexi Saturday":"FS",
        "Flexi Public Holiday":"FPH"
	}


    for emp in employees:
        for date in date_range:
            relieving_date_change = None
            if emp.get('relieving_date'):
                change_date_rel = datetime.strptime(date,"%Y-%m-%d").date()
                relieving_date_change = emp.get('relieving_date') >= change_date_rel
            else:
                relieving_date_change = True

            change_date = datetime.strptime(date,"%Y-%m-%d").date()
            if emp.get("date_of_joining") <= change_date and relieving_date_change:
                
                checkins = frappe.get_all('Employee Checkin', filters=[
                    ['employee', '=', emp['name']],
                    ['time', 'between', [date + ' 00:00:00', date + ' 23:59:59']]
                ], fields=['time', 'log_type'])
                in_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'IN'), None)
                out_time = next((chk['time'] for chk in checkins if chk['log_type'] == 'OUT'), None)
                shift = checkins[0]['shift'] if checkins and 'shift' in checkins[0] else None
                working_hours = calculate_working_hours(in_time, out_time)
                working_hours_threshold = get_working_hours_threshold(shift)
                status = determine_status(in_time, out_time,working_hours,working_hours_threshold, leave_details,holiday_details, emp['name'], date,leave_type_short_forms)

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

def determine_status(in_time, out_time, working_hours, working_hours_threshold, leave_details, holiday_details, employee, date,leave_type_short_forms):
    if employee in leave_details and date in leave_details[employee]:
        leave_type = leave_details[employee][date]
        
        return leave_type_short_forms[leave_type]

    if employee in holiday_details and date in holiday_details[employee]:
        return holiday_details[employee][date]
    if not in_time and not out_time:
        return 'Missing Punches'
    if not in_time:
        return 'MI'
    if not out_time:
        return 'MO'
    
    if working_hours:
        hours, minutes = map(int, working_hours.split(':'))
        if hours + minutes / 60 >= working_hours_threshold:
            return 'P'
    return 'A'

def get_working_hours_threshold(shift):
    if not shift:
        return 6  # Default threshold if no shift is provided
    shift_doc = frappe.get_doc('Shift Type', shift)
    return shift_doc.working_hours_threshold_for_absent or 6  # Default to 6 if not specified in the shift

def generate_actions(status, employee, date):
    if status == "Missing Punches":
        return f'<a href="#" onclick="openPopup(\'{employee}\', \'{date}\')">Add Checkin Checkouts</a>'
    elif status == "MI":
        return f'<a href="#" onclick="openPopupforcheckin(\'{employee}\', \'{date}\')">Add Checkin</a>'
    elif status == "MO":
        return f'<a href="#" onclick="openPopupforcheckout(\'{employee}\', \'{date}\')">Add Checkout</a>'
    return ''

def get_leave_dates(filters):
    print('Holidays details')
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    if not start_date or not end_date:
        return {}

    leave_data = frappe.get_all("Attendance", filters={"attendance_date": ["between", [start_date, end_date]],"docstatus":1}, fields=["employee", "attendance_date", "status", "leave_type"])
    
    leave_details = {}
    for entry in leave_data:
        if entry.get("status") == "On Leave":
            date = getdate(entry["attendance_date"]).strftime("%Y-%m-%d")
            leave_type = entry.get("leave_type")
            employee = entry["employee"]
            if employee not in leave_details:
                leave_details[employee] = {}
            leave_details[employee][date] = f"{leave_type}" if leave_type else "On Leave"
    
    
    return leave_details

def get_holiday_dates(filters, employees):
    print('Holidays details')
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
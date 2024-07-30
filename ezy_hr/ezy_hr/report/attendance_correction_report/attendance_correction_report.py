# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt


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
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 160},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 160},
        {"label": "Date", "fieldname": "attendance_date", "fieldtype": "Date", "width": 110},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Data", "width": 160},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Data", "width": 160},
        {"label": "Working Hours", "fieldname": "working_hours", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
         {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 130},
        {"label": "Actions", "fieldname": "add_checkin", "fieldtype": "Data", "width": 180},
    ]

def get_data(filters):
    final_data = []
    if filters.get('from_date') and filters.get('to_date'):
        from_date = getdate(filters['from_date'])
        to_date = getdate(filters['to_date'])
        date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]
        employees = None
        
        if filters.get("employee"):
            employees = frappe.db.get_list("Employee", filters={"employee": filters.get("employee"),"company":filters.get("company")},fields=["name", "employee_name","designation","department","date_of_joining"])
        else:
            employees = frappe.db.get_list("Employee", filters={"company":filters.get("company")},fields=["name", "employee_name","designation","department","date_of_joining"])
            
        for employee in employees:
            for single_date in date_range:
                single_date_str = single_date.strftime('%Y-%m-%d')
                attendance_record = frappe.db.get_list("Attendance", 
                    filters={"employee": employee["name"], "attendance_date": single_date_str,"docstatus":["!=",2]}, 
                    fields=['employee', 'employee_name', 'attendance_date', 'working_hours', 'in_time', 'out_time', 'status', 'docstatus','leave_type'])
                
                if attendance_record:
                    for record in attendance_record:
                        if record.get("docstatus") == 0:
                            record["status"] = "Absent"
                        if not record.get("out_time"):
                            record["out_time"] = "MO"
                        record["add_checkin"] = add_checkin_missing(record)
                        department_name = None
                        if employee["department"]:
                            department_name = employee["department"].split(" - ")[0] if " - " in employee["department"] else employee["department"]
                        record.update({
                            "department":department_name if department_name else None,
                            'designation':employee['designation'],
                            "date_of_joining":employee["date_of_joining"],
                        })
                        final_data.append(record)
                else:
                    department_name = None
                    if employee["department"]:
                        department_name = employee["department"].split(" - ")[0] if " - " in employee["department"] else employee["department"]
                    final_data.append({
                        "employee": employee["name"],
                        "employee_name": employee["employee_name"],
                        "department":department_name if department_name else None,
                        'designation':employee['designation'],
                        "date_of_joining":employee["date_of_joining"],
                        "attendance_date": single_date_str,
                        "working_hours": "0:00",
                        "in_time": None,
                        "out_time": None,
                        "status": "Absent",
                        "add_checkin": add_checkin_missing({"out_time": "MO", "employee": employee["name"], "attendance_date": single_date_str})
                    })
    
    return final_data

def add_checkin_missing(record):
    if record['out_time'] == 'MO':
        return f'<a href="#" onclick="openPopup(\'{record["employee"]}\', \'{record["attendance_date"]}\')">Add Checkin Checkouts</a>'
    return ''

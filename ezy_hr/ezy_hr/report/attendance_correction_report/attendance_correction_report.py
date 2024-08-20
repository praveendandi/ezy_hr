# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt



import frappe
from frappe.utils import getdate
from datetime import timedelta


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 110},
        {"label": "Date", "fieldname": "attendance_date", "fieldtype": "Date", "width": 110},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Data", "width": 160},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Data", "width": 160},
        {"label": "Working Hours", "fieldname": "working_hours", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 130},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 130},
        {"label": "Actions", "fieldname": "add_checkin", "fieldtype": "Data", "width": 180},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 160},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 160},
    ]

def get_data(filters):
    final_data = []
    leave_type_short_forms = frappe.get_list("Leave Type", ['name', 'custom_abbreviation'])
    leave_type_abbr = {item['name']: item['custom_abbreviation'] for item in leave_type_short_forms}

    from_date = getdate(filters.get('from_date'))
    to_date = getdate(filters.get('to_date'))
    date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]

    employees = get_employees(filters)

    for employee in employees:
        for single_date in date_range:
            if employee.get('relieving_date') and employee.get('relieving_date') < single_date:
                continue

            single_date_str = single_date.strftime('%Y-%m-%d')
            holiday_days = get_holiday_days(employee)

            if employee.get("date_of_joining") <= single_date:
                attendance_record = frappe.db.get_list("Attendance", 
                    filters={"employee": employee["name"], "attendance_date": single_date_str, "docstatus": ["!=", 2]}, 
                    fields=['employee', 'employee_name', 'attendance_date', 'working_hours', 'in_time', 'out_time', 'status', 'docstatus', 'leave_type'])
                
                if attendance_record:
                    for record in attendance_record:
                        if record.get("leave_type"):
                            record["leave_type"] = leave_type_abbr.get(record["leave_type"], record["leave_type"])

                        if single_date in holiday_days and not record:
                            record["status"] = "Sunday"
                        elif record.get("docstatus") == 0:
                            record["status"] = "Absent" if 0 < record.get("working_hours", 0) < 6 else "MO"
                        
                        record["add_checkin"] = add_checkin_missing(record)
                        
                        department_name = employee["department"].split(" - ")[0] if employee["department"] else None
                        record.update({
                            "department": department_name,
                            'designation': employee['designation'],
                            "date_of_joining": employee["date_of_joining"],
                        })
                        final_data.append(record)
                else:
                    status = "Sunday" if single_date in holiday_days else "Absent"
                    department_name = employee["department"].split(" - ")[0] if employee["department"] else None
                    final_data.append({
                        "employee": employee["name"],
                        "employee_name": employee["employee_name"],
                        "department": department_name,
                        'designation': employee['designation'],
                        "date_of_joining": employee["date_of_joining"],
                        "attendance_date": single_date_str,
                        "working_hours": "0:00",
                        "in_time": None,
                        "out_time": None,
                        "status": status,
                        "add_checkin": add_checkin_missing({"working_hours": "0.00", "out_time": None, "employee": employee["name"], "attendance_date": single_date_str})
                    })
    frappe.log_error("final_data", final_data)
    return final_data

def get_employees(filters):
    if filters.get("employee"):
        return frappe.db.get_list("Employee", filters={"employee": filters.get("employee"), "company": filters.get("company")}, fields=["name", "employee_name", "designation", "department", "date_of_joining", "holiday_list", "relieving_date"])
    elif filters.get("reports")=="My Team":
        logged_in_employee = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
        return frappe.db.get_list("Employee", filters={"reports_to": logged_in_employee, "company": filters.get("company")}, fields=["name", "employee_name", "designation", "department", "date_of_joining", "holiday_list", "relieving_date"])
    else:
        return frappe.db.get_list("Employee", filters={"company": filters.get("company")}, fields=["name", "employee_name", "designation", "department", "date_of_joining", "holiday_list", "relieving_date"])

def add_checkin_missing(record):
    if record.get('out_time') is None or record.get("working_hours", 0) < 6:
        return f'<a href="#" onclick="openPopup(\'{record["employee"]}\', \'{record["attendance_date"]}\')">Add Checkin/Checkout</a>'
    return ''

def get_holiday_days(employee):
    holidays = frappe.db.get_list("Holiday", filters={"parent": employee["holiday_list"]}, fields=["holiday_date"], ignore_permissions=True)
    return [each.get("holiday_date") for each in holidays]

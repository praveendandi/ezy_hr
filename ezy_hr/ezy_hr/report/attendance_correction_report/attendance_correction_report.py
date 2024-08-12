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
        {"label": "Date", "fieldname": "attendance_date", "fieldtype": "Date", "width": 110},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Data", "width": 160},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Data", "width": 160},
        {"label": "Working Hours", "fieldname": "working_hours", "fieldtype": "Data", "width": 90},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 70},
        {"label": "Attendance Request", "fieldname": "attendance_request", "fieldtype": "Data","width":4,"hidden":1},
        {"label": "Actions", "fieldname": "add_checkin", "fieldtype": "Data", "width": 180},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 160},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 160},
    ]

def get_data(filters):
    final_data = []
    leave_type_short_forms = frappe.get_list("Leave Type",['name','custom_abbreviation'])
    leave_type_abbr = {item['name']: item['custom_abbreviation'] for item in leave_type_short_forms}

    if filters.get('from_date') and filters.get('to_date'):
        from_date = getdate(filters['from_date'])
        to_date = getdate(filters['to_date'])
        date_range = [from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)]
        employees = None
        
        if filters.get("employee"):
            employees = frappe.db.get_list("Employee", filters={"employee": filters.get("employee"),"company":filters.get("company")},fields=["name", "employee_name","designation","department","date_of_joining","holiday_list","relieving_date"])
        else:
            employees = frappe.db.get_list("Employee", filters={"company":filters.get("company")},fields=["name", "employee_name","designation","department","date_of_joining","holiday_list","relieving_date"])
       
        for employee in employees:
            for single_date in date_range:
                if employee.get('relieving_date'):
                    relieving_date_change = employee.get('relieving_date') >= single_date
                else:
                    relieving_date_change = True

                single_date_str = single_date.strftime('%Y-%m-%d')
                hoidaylist_data = holiday_list(employee)

                if employee.get("date_of_joining") <= single_date and relieving_date_change:
                    attendance_record = frappe.db.get_list("Attendance", 
                        filters={"employee": employee["name"], "attendance_date": single_date_str,"docstatus":["!=",2]}, 
                        fields=['employee', 'employee_name', 'attendance_date', 'working_hours', 'in_time', 'out_time', 'status', 'docstatus','leave_type', 'attendance_request'])
                    
                    if attendance_record:
                        for record in attendance_record:
                            # frappe.log_error("record",record)
                            if record.get("leave_type"):
                                record["leave_type"] = leave_type_abbr.get(record["leave_type"], record["leave_type"])
                                # record["status"] = leave_type_abbr.get(record["leave_type"], record["status"])

                            if single_date in hoidaylist_data and not record:
                                record["status"] = "Sunday"

                            if record.get("docstatus") == 0:
                                
                                if 0 < record.get("working_hours",0) < 6:
                                    record["status"] = "Absent"
                                else:
                                    record["status"] = "MO"
                            if record.get("attendance_request"):
                                onduty = frappe.db.get_list("Attendance Request",{"name":record.get("attendance_request")},["name","reason"])
                                record["status"] = onduty[0]["reason"]
                                frappe.log_error("onduty",onduty)
                                # add_checkin_missing(record)
                            # if not record.get("out_time") and record.get("status") != "On Leave":
                            #     record["out_time"] = "MO"
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
                        if single_date in hoidaylist_data:
                            status = "Sunday"
                        else:
                            status = "Absent"
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
                            "status":status,
                            "add_checkin": add_checkin_missing({"working_hours":"0.00","out_time": None, "employee": employee["name"], "attendance_date": single_date_str})
                        })
    frappe.log_error("final_data",final_data)
    return final_data

def add_checkin_missing(record):
    if record['out_time'] == None :
        return f'<a href="#" onclick="openPopup(\'{record["employee"]}\', \'{record["attendance_date"]}\')">Add Checkin Checkouts</a>'
    if record["working_hours"] < 6:
        return f'<a href="#" onclick="openPopup(\'{record["employee"]}\', \'{record["attendance_date"]}\')">Add Checkin Checkouts</a>'

    return ''


def holiday_list(employee):

    holiday_list = frappe.db.get_list("Holiday",filters={"parent":employee["holiday_list"]},fields=["description","holiday_date"],ignore_permissions=True)

    holiday_days = [each.get("holiday_date") for each in holiday_list]

    return holiday_days

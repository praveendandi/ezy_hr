# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

# import frappe



# import frappe
# from datetime import datetime, timedelta
# from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data

# def get_leave_dates(filters):
#     leave_data = frappe.get_all("Leave Application", filters={"employee": filters.get("employee"), 
#                                                               "status": "Approved",
#                                                               "from_date": (">=", filters.get("from_date")),
#                                                               "to_date": ("<=", filters.get("to_date"))},
#                                  fields=["from_date"])
#     leave_dates = [datetime.strftime(entry["from_date"], "%Y-%m-%d") for entry in leave_data if entry["from_date"] is not None]
#     return leave_dates

# def get_missing_checkout_dates(filters):
#     missing_checkout_data = frappe.get_all("Attendance", filters={"employee": filters.get("employee"),
#                                                                   "status": "Check-Out Is Missing",
#                                                                   "attendance_date": (">=", filters.get("from_date")),
#                                                                   "attendance_date": ("<=", filters.get("to_date"))},
#                                            fields=["attendance_date"])
#     missing_checkout_dates = [datetime.strftime(entry["attendance_date"], "%Y-%m-%d") for entry in missing_checkout_data if entry["attendance_date"] is not None]
#     return missing_checkout_dates


# def execute(filters=None):
#     source_data = get_source_data(filters)
#     if source_data is None:
        
import frappe
from datetime import datetime, timedelta
# from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data
from ezy_hr.ezy_hr.report.employee_checkins_and_checkouts.employee_checkins_and_checkouts import get_data as source_get_data
def get_leave_dates(filters):
    leave_data = frappe.get_all("Leave Application", filters={"employee": filters.get("employee"), 
                                                              "status": "Approved",
                                                              "from_date": (">=", filters.get("from_date")),
                                                              "to_date": ("<=", filters.get("to_date"))},
                                 fields=["from_date"])
    leave_dates = [datetime.strftime(entry["from_date"], "%Y-%m-%d") for entry in leave_data if entry["from_date"] is not None]
    return leave_dates

def get_missing_checkout_dates(filters):
    missing_checkout_data = frappe.get_all("Attendance", filters={"employee": filters.get("employee"),
                                                                  "status": "Check-Out Is Missing",
                                                                  "attendance_date": (">=", filters.get("from_date")),
                                                                  "attendance_date": ("<=", filters.get("to_date"))},
                                           fields=["attendance_date"])
    missing_checkout_dates = [datetime.strftime(entry["attendance_date"], "%Y-%m-%d") for entry in missing_checkout_data if entry["attendance_date"] is not None]
    return missing_checkout_dates


def execute(filters=None):
    source_data = get_source_data(filters)
    if source_data is None:
        frappe.msgprint("Failed to retrieve source data.")
        return [], []

    leave_dates = get_leave_dates(filters)
    missing_checkout_dates = get_missing_checkout_dates(filters)
    
    # Create a dictionary to store the status for each date
    status_by_date = {}
    for entry in source_data:
        date = entry.get("date")
        status = entry.get("status")
        if date:
            date_str = datetime.strftime(date, "%Y-%m-%d")
            if date_str not in status_by_date:
                status_by_date[date_str] = {}
            status_by_date[date_str][entry.get("employee")] = status
    
    # Get the unique set of all dates in the report period
    all_dates = set(status_by_date.keys())
    all_dates.update(leave_dates)
    all_dates.update(missing_checkout_dates)
    
    # Sort the dates
    all_dates = sorted(all_dates)
    
    # Define columns
    columns = [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150}
    ]
    
    # Add date columns
    for date_str in all_dates:
        columns.append({"label": date_str, "fieldname": date_str, "fieldtype": "Data", "width": 100})
    
    # Prepare data rows
    employee_data = {}
    for entry in source_data:
        employee_id = entry.get("employee")
        employee_name = entry.get("employee_name")
        date_obj = entry.get("date")
        date_str = datetime.strftime(date_obj, "%Y-%m-%d") if date_obj is not None else ""

        if employee_id:
            if employee_id not in employee_data:
                employee_data[employee_id] = {"employee": employee_id, "employee_name": employee_name}
                for date in all_dates:
                    employee_data[employee_id][date] = status_by_date.get(date, {}).get(employee_id, "Missing Log")
            else:
                for date in all_dates:
                    if date not in employee_data[employee_id]:
                        employee_data[employee_id][date] = status_by_date.get(date, {}).get(employee_id, "Missing Log")
    
    data = list(employee_data.values())
    
    return columns, data

def get_source_data(filters):
    source_data = source_get_data(filters)
    return source_data
    
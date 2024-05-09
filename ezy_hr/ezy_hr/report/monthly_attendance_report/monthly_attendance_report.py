# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt

# # import frappe



# # import frappe
# # from datetime import datetime, timedelta
# # from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data

# # def get_leave_dates(filters):
# #     leave_data = frappe.get_all("Leave Application", filters={"employee": filters.get("employee"), 
# #                                                               "status": "Approved",
# #                                                               "from_date": (">=", filters.get("from_date")),
# #                                                               "to_date": ("<=", filters.get("to_date"))},
# #                                  fields=["from_date"])
# #     leave_dates = [datetime.strftime(entry["from_date"], "%Y-%m-%d") for entry in leave_data if entry["from_date"] is not None]
# #     return leave_dates

# # def get_missing_checkout_dates(filters):
# #     missing_checkout_data = frappe.get_all("Attendance", filters={"employee": filters.get("employee"),
# #                                                                   "status": "Check-Out Is Missing",
# #                                                                   "attendance_date": (">=", filters.get("from_date")),
# #                                                                   "attendance_date": ("<=", filters.get("to_date"))},
# #                                            fields=["attendance_date"])
# #     missing_checkout_dates = [datetime.strftime(entry["attendance_date"], "%Y-%m-%d") for entry in missing_checkout_data if entry["attendance_date"] is not None]
# #     return missing_checkout_dates


# # def execute(filters=None):
# #     source_data = get_source_data(filters)
# #     if source_data is None:
        
# import frappe
# from datetime import datetime, timedelta
# # from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data
# from ezy_hr.ezy_hr.report.employee_checkins_and_checkouts.employee_checkins_and_checkouts import get_data as source_get_data
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
#         frappe.msgprint("Failed to retrieve source data.")
#         return [], []

#     leave_dates = get_leave_dates(filters)
#     missing_checkout_dates = get_missing_checkout_dates(filters)
    
#     # Create a dictionary to store the status for each date
#     status_by_date = {}
#     for entry in source_data:
#         date = entry.get("date")
#         status = entry.get("status")
#         if date:
#             date_str = datetime.strftime(date, "%Y-%m-%d")
#             if date_str not in status_by_date:
#                 status_by_date[date_str] = {}
#             status_by_date[date_str][entry.get("employee")] = status
    
#     # Get the unique set of all dates in the report period
#     all_dates = set(status_by_date.keys())
#     all_dates.update(leave_dates)
#     all_dates.update(missing_checkout_dates)
    
#     # Sort the dates
#     all_dates = sorted(all_dates)
    
#     # Define columns
#     columns = [
#         {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
#         {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150}
#     ]
    
#     # Add date columns
#     for date_str in all_dates:
#         columns.append({"label": date_str, "fieldname": date_str, "fieldtype": "Data", "width": 100})
    
#     # Prepare data rows
#     employee_data = {}
#     for entry in source_data:
#         employee_id = entry.get("employee")
#         employee_name = entry.get("employee_name")
#         date_obj = entry.get("date")
#         date_str = datetime.strftime(date_obj, "%Y-%m-%d") if date_obj is not None else ""

#         if employee_id:
#             if employee_id not in employee_data:
#                 employee_data[employee_id] = {"employee": employee_id, "employee_name": employee_name}
#                 for date in all_dates:
#                     employee_data[employee_id][date] = status_by_date.get(date, {}).get(employee_id, "Missing Log")
#             else:
#                 for date in all_dates:
#                     if date not in employee_data[employee_id]:
#                         employee_data[employee_id][date] = status_by_date.get(date, {}).get(employee_id, "Missing Log")
    
#     data = list(employee_data.values())
    
#     return columns, data

# def get_source_data(filters):
#     source_data = source_get_data(filters)
#     return source_data
    
# import frappe
# from datetime import datetime
# from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data

# def get_leave_dates(filters):
#     start_date = filters.get("from_date")
#     end_date = filters.get("to_date")
    
#     if not start_date or not end_date:
#         return []

#     leave_data = frappe.get_all("Leave Application", filters={"employee": filters.get("employee"), 
#                                                               "status": "Approved",
#                                                               "from_date": (">=", start_date),
#                                                               "to_date": ("<=", end_date)},
#                                  fields=["from_date"])
#     leave_dates = [entry["from_date"].strftime("%Y-%m-%d") for entry in leave_data]
#     print("Leave Dates:", leave_dates)
#     return leave_dates


# def get_missing_checkout_dates(filters):
#     missing_checkout_data = frappe.get_all("Attendance", filters={"employee": filters.get("employee"),
#                                                                   "status": "Check-Out Is Missing",
#                                                                   "attendance_date": (">=", filters.get("from_date")),
#                                                                   "attendance_date": ("<=", filters.get("to_date"))},
#                                            fields=["attendance_date"])
#     missing_checkout_dates = [entry["attendance_date"] for entry in missing_checkout_data]
#     return missing_checkout_dates

# from datetime import datetime, timedelta
# import datetime as dt

# def execute(filters=None):
#     print("Filter Dates:", filters.get("from_date"), "-", filters.get("to_date"))

#     source_data = get_source_data(filters)
#     if source_data is None:
#         frappe.msgprint("Failed to retrieve source data.")
#         return [], []

#     leave_dates = get_leave_dates(filters)
#     print("Leave Dates:", leave_dates)

#     employee_data = {}
#     for entry in source_data:
#         employee_id = entry.get("employee")
#         employee_name = entry.get("employee_name")
#         if employee_id:
#             if employee_id not in employee_data:
#                 employee_data[employee_id] = {
#                     "employee_id": employee_id,
#                     "employee_name": employee_name,
#                     "status_by_date": {}
#                 }
#             date = entry.get("date")
#             status = entry.get("status")
#             if isinstance(date, dt.date):
#                 date_str = date.strftime("%Y-%m-%d")
#             else:
#                 date_str = date
#             employee_data[employee_id]["status_by_date"][date_str] = status

#     print("Employee Data Before Adding Leave Dates:", employee_data)

#     # Add leave dates to employee data
#     for employee_id, data_row in employee_data.items():
#         for leave_date in leave_dates:
#             if leave_date not in data_row["status_by_date"]:
#                 data_row["status_by_date"][leave_date] = "On Leave"

#     print("Employee Data After Adding Leave Dates:", employee_data)

#     columns = [
#         {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
#         {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150}
#     ]

#     all_dates = []
#     current_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
#     end_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
#     while current_date <= end_date:
#         all_dates.append(current_date.strftime("%Y-%m-%d"))
#         current_date += timedelta(days=1)

#     for date_str in all_dates:
#         # Format the date to display only the day of the month
#         formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d")
#         columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 100})
#         print("Added column:", formatted_date)

#     columns.extend([
#         {"label": "Total Present", "fieldname": "total_present", "fieldtype": "Data", "width": 100},
#         {"label": "Total Leave", "fieldname": "total_leave", "fieldtype": "Data", "width": 100}
#     ])

#     data = []
#     for employee_id, data_row in employee_data.items():
#         row = {"employee": data_row["employee_id"], "employee_name": data_row["employee_name"]}
#         total_present = sum(1 for status in data_row["status_by_date"].values() if status == "P")
#         total_leave = sum(1 for status in data_row["status_by_date"].values() if status == "On Leave")
#         row["total_present"] = total_present 
#         row["total_leave"] = total_leave 
#         for date_str, status in data_row["status_by_date"].items():
#             row[date_str] = status
#         for date_str in all_dates:
#             if date_str not in row:
#                 row[date_str] = ""  # Add empty value for dates without data
#         data.append(row)

#     return columns, data


# def get_source_data(filters):
#     source_data = source_get_data(filters)
#     return source_data

import frappe
from datetime import datetime
from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data

def get_leave_dates(filters):
    start_date = filters.get("from_date")
    end_date = filters.get("to_date")
    
    if not start_date or not end_date:
        return {}

    leave_data = frappe.get_all("Leave Application", filters={"employee": filters.get("employee"), 
                                                              "status": "Approved",
                                                              "from_date": (">=", start_date),
                                                              "to_date": ("<=", end_date)},
                                 fields=["from_date", "to_date", "leave_type"])
    
    leave_details = {}
    for entry in leave_data:
        from_date = entry["from_date"]
        to_date = entry["to_date"]
        leave_type = entry["leave_type"]
        current_date = from_date
        while current_date <= to_date:
            leave_details[current_date.strftime("%Y-%m-%d")] = "On Leave - " + leave_type
            current_date += timedelta(days=1)
            
    print("Leave Details:", leave_details)
    return leave_details



def get_missing_checkout_dates(filters):
    missing_checkout_data = frappe.get_all("Attendance", filters={"employee": filters.get("employee"),
                                                                  "status": "Check-Out Is Missing",
                                                                  "attendance_date": (">=", filters.get("from_date")),
                                                                  "attendance_date": ("<=", filters.get("to_date"))},
                                           fields=["attendance_date"])
    missing_checkout_dates = [entry["attendance_date"] for entry in missing_checkout_data]
    return missing_checkout_dates

from datetime import datetime, timedelta
import datetime as dt

def execute(filters=None):
    print("Filter Dates:", filters.get("from_date"), "-", filters.get("to_date"))

    source_data = get_source_data(filters)
    if source_data is None:
        frappe.msgprint("Failed to retrieve source data.")
        return [], []

    employee_data = {}
    for entry in source_data:
        employee_id = entry.get("employee")
        employee_name = entry.get("employee_name")
        # department = entry.get("department")
        date_of_joining = entry.get("date_of_joining")
        designation = entry.get("designation")
        department_name = None
        if entry.get("department"):
            department_name = entry.get("department").split(" - ")[0] if " - " in entry.get("department") else entry.get("department")    
        if employee_id:
            if employee_id not in employee_data:
                employee_data[employee_id] = {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "department": department_name,
                    "date_of_joining":date_of_joining,
                    "designation":designation,
                    "status_by_date": {}
                }
            date = entry.get("date")
            status = entry.get("status")
            leave_details = get_leave_dates(filters)
            if isinstance(date, dt.date):
                date_str = date.strftime("%Y-%m-%d")
            else:
                date_str = date
            employee_data[employee_id]["status_by_date"][date_str] = status

            for dates, leave in leave_details.items():
                employee_data[employee_id]["status_by_date"][dates] = leave

    # Get all leave types available in the system
    all_leave_types = frappe.get_all("Leave Type", fields=["name"])

    # Define mapping for short leave type labels
    leave_type_short_forms = {
        "Weekly Off": "Wo",
        "Casual Leave": "CL",
        "Sick Leave": "SL",
        "Privilege Leave": "PL",
        "Maternity Leave": "ML",
        "Compensatory Off (COL)": "COL",
        "Compensatory Off": "COL",
        "Accident Leave on shift": "ALS",
        "Leave Without Pay": "LWP",
        "ESI Leave": "ESIL",
        "Holiday": "HD",
        "Unpaid Leave": "UNL"
    }

    # Initialize leave type counts to zero
    leave_types = {leave_type_short_forms.get(leave_type["name"], leave_type["name"]): 0 for leave_type in all_leave_types}

    # Calculate total leave used for each leave type
    for leave_date, leave_type in leave_details.items():
        if "On Leave" in leave_type:
            leave_type = leave_type.split(" - ")[1]
            leave_types[leave_type_short_forms.get(leave_type, leave_type)] += 1

    columns = [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Data", "width": 150},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150}
    ]

    # Create a list of dates within the selected date range
    all_dates = []
    current_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
    end_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
    while current_date <= end_date:
        all_dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    # Add columns for each date within the selected date range
    # for date_str in all_dates:
    #     # Format the date to display only the day of the month
    #     formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d")
    #     columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 100})
    # Add columns for each date within the selected date range
    for date_str in all_dates:
        # Format the date to display the day along with the date
        formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a %d")
        columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 90})

    # Add columns for total leave used for each leave type
    for leave_type, leave_count in leave_types.items():
        columns.append({"label": f"{leave_type}", "fieldname": leave_type.lower().replace(" ", "_") + "_leave_used", "fieldtype": "Data", "width": 50})

    # Add MO and MI columns for total count
    columns.extend([
        {"label": "MO", "fieldname": "morning_shift_total", "fieldtype": "Data", "width": 50},
        {"label": "MI", "fieldname": "mid_shift_total", "fieldtype": "Data", "width": 50},
        {"label": "A", "fieldname": "total_empty_columns", "fieldtype": "Data", "width": 50},
        {"label": "Total", "fieldname": "total_selected_dates", "fieldtype": "Data", "width": 100},
        {"label": "Total Payable Days", "fieldname": "total_payable_days", "fieldtype": "Data", "width": 100},
    ])

    data = []
    for employee_id, data_row in employee_data.items():

        row = {"employee": data_row["employee_id"], "employee_name": data_row["employee_name"] , "department": data_row["department"],"date_of_joining":data_row["date_of_joining"],"designation":data_row["designation"]}
        total_present = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "P" and date_str in all_dates)
        total_leave = sum(1 for date_str, status in data_row["status_by_date"].items() if "On Leave" in status and date_str in all_dates)
        morning_shift_total = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "MO" and date_str in all_dates)
        mid_shift_total = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "MI" and date_str in all_dates)


        row["morning_shift_total"] = morning_shift_total
        row["mid_shift_total"] = mid_shift_total
        row["total_present"] = total_present
        row["total_leave"] = total_leave

        # Add total selected dates count
        total_selected_dates_count = len(all_dates)
        row["total_selected_dates"] = total_selected_dates_count

        # Calculate total empty columns count
        total_empty_columns_count = total_selected_dates_count - len(data_row["status_by_date"])
        row["total_empty_columns"] = total_empty_columns_count

        # Calculate total payable days
        total_payable_days = total_selected_dates_count - total_empty_columns_count
        row["total_payable_days"] = total_payable_days

        # Add leave details for each date within the selected date range
        for date_str in all_dates:
            status = data_row["status_by_date"].get(date_str, "")
            row[date_str] = status

        # Add total leave used for each leave type
        for leave_type, leave_count in leave_types.items():
            row[leave_type.lower().replace(" ", "_") + "_leave_used"] = leave_count

        data.append(row)

    return columns, data


def get_employee_holidays(employee_id, from_date, to_date):
    # Fetch employee's holiday list
    employee_holiday_list = frappe.get_value("Employee", employee_id, "holiday_list")

    # Fetch holidays from the holiday list within the selected date range
    holidays = frappe.get_all("Holiday", filters={"parent": employee_holiday_list, "holiday_date": [">=", from_date], "holiday_date": ["<=", to_date]}, fields=["holiday_date"])
    holiday_dates = [holiday.get("holiday_date").strftime("%Y-%m-%d") for holiday in holidays]
    return holiday_dates


def get_source_data(filters):
    source_data = source_get_data(filters)
    return source_data

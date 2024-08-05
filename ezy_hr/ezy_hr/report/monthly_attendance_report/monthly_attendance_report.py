# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, formatdate
# from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data
from ezy_hr.ezy_hr.report.attendance_correction_report.attendance_correction_report import get_data as source_get_data

def execute(filters=None):
    try:
        # Retrieve the source data based on the provided filters
        source_data = source_get_data(filters)
        if source_data is None:
            frappe.msgprint("Failed to retrieve source data.")
            return [], []
        
        all_leave_types = frappe.get_all("Leave Type", fields=["name","custom_abbreviation"])
        
        # Initialize leave_type_short_forms correctly
        leave_type_short_forms = {}
        for leave_type in all_leave_types:
            leave_type_short_forms[leave_type['name']] = leave_type['custom_abbreviation']
        
        leave_types = {leave_type['custom_abbreviation']: 0 for leave_type in all_leave_types}
        frappe.log_error("leave arr....",leave_types)
        # Define columns
        columns = [
            {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
            {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
            {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
            {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150},
            {"label": "DOJ", "fieldname": "date_of_joining", "fieldtype": "Data", "width": 150},
        ]

        # Add columns for each date within the selected date range
        all_dates = []
        current_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            all_dates.append(date_str)
            formatted_date = current_date.strftime("%a %d")
            columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 90})
            current_date += timedelta(days=1)

        # Process source data and prepare final data
        for leave_type, leave_count in leave_types.items():
            columns.append({"label": f"{leave_type}", "fieldname": leave_type, "fieldtype": "Data", "width": 50})

        columns.extend([
            {"label": "A", "fieldname": "total_empty_columns", "fieldtype": "Data", "width": 50},
            {"label": "P", "fieldname": "total_present", "fieldtype": "Data", "width": 100},
            {"label": "L", "fieldname": "total_leave", "fieldtype": "Data", "width": 100},
            {"label": "Wo", "fieldname": "wo", "fieldtype": "Data", "width": 100},
            {"label": "Total", "fieldname": "total_selected_dates", "fieldtype": "Data", "width": 100},
            {"label": "Total Payable Days", "fieldname": "total_payable_days", "fieldtype": "Data", "width": 100},
        ])

        data_dict = {}
        status_short_forms = {
            "Present": "P",
            "Absent": "A",
            "Sunday": "WO",
            "On Leave": 'L',
            "MO": "MO",
        }

        for entry in source_data:
            employee_id = entry.get("employee")
            if employee_id not in data_dict:
                data_dict[employee_id] = {
                    "employee": employee_id,
                    "employee_name": entry.get("employee_name"),
                    "department": entry.get("department"),
                    "designation": entry.get("designation"),
                    "date_of_joining": entry.get("date_of_joining"),
                }
            attendance = entry.get('attendance_date')
            if isinstance(attendance,str):
                data_dict[employee_id].update({entry.get('attendance_date'):status_short_forms.get(entry.get("status"))})
                if entry.get("leave_type"):
                    data_dict[employee_id].update({entry.get('attendance_date'):entry.get("leave_type")})
                    if not entry.get("leave_type") in  data_dict[employee_id]:
                        data_dict[employee_id].update({entry.get("leave_type"):0})
                    data_dict[employee_id][entry.get("leave_type")] +=1
            else:
                date_str = entry.get('attendance_date').strftime("%Y-%m-%d")
                data_dict[employee_id].update({date_str:status_short_forms.get(entry.get("status"))})

                if entry.get("leave_type"):
                    
                    data_dict[employee_id].update({date_str:entry.get("leave_type")})
                    if not entry.get("leave_type") in  data_dict[employee_id]:
                        data_dict[employee_id].update({entry.get("leave_type"):0})
                    data_dict[employee_id][entry.get("leave_type")] +=1
                
        data = list(data_dict.values())

        get_counts(data,all_dates,leave_types)

        sort_data = sorted(data, key=lambda x: x["date_of_joining"],reverse=False)

        return columns, sort_data
    
    except Exception as e:
        frappe.log_error("attendnace error",str(e))


def get_counts(data,all_dates,leave_types):

    total_present = 0
    total_leave = 0
    total_absent = 0
    wo  = 0
    frappe.log_error("final data f...",data)
    for data_row in data:
        
        total_present = sum(1 for key, value in data_row.items() if value == "P" and key in all_dates)
        
        total_leave = sum(1 for key, value in data_row.items() if (value in leave_types and value != "WO") and key in all_dates)

        total_absent = sum(1 for key, value in data_row.items() if value == "A" and key in all_dates)

        wo = sum(1 for key, value in data_row.items() if value == "WO" and key in all_dates)
        # Add total selected dates count
        data_row['total_present'] = total_present
        data_row['total_empty_columns'] = total_absent
        data_row['total_leave'] = total_leave
        data_row['wo'] = wo
        
        total_selected_dates_count = len(all_dates)
        total_payable_days = total_present + total_leave + wo
        data_row['total_selected_dates'] = total_selected_dates_count
        data_row['total_payable_days'] = total_payable_days
    
        # for key, value in data_row.items():
        #     if leave_types.get(key,None):
        #         data_row[leave_types.get(key, key)] = value
        

# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt


import frappe
from datetime import datetime
from frappe.utils import flt, formatdate
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
   
	# Retrieve the source data based on the provided filters
	source_data = get_source_data(filters)
	if source_data is None:
		frappe.msgprint("Failed to retrieve source data.")
		return [], []

	employee_data = {}
	
	# Process each entry in the source data
	for entry in source_data:
		employee_id = entry.get("employee")
		employee_name = entry.get("employee_name")
		department = entry.get("department")
		
		if employee_id:
			if employee_id not in employee_data:
				employee_data[employee_id] = {
					"employee_id": employee_id,
					"employee_name": employee_name,
					"department": department,
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
				if isinstance(dates, dt.date):
					employee_data[employee_id]["status_by_date"][dates.strftime("%Y-%m-%d")] = leave

	# Get all leave types available in the system
	all_leave_types = frappe.get_all("Leave Type", fields=["name"])

	employee_data = {}
	for entry in source_data:
		employee_id = entry.get("employee")
		employee_name = entry.get("employee_name")
		department = entry.get("department")
		if employee_id:
			if employee_id not in employee_data:
				employee_data[employee_id] = {
					"employee_id": employee_id,
					"employee_name": employee_name,
					"department": department,
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

	leave_types = {leave_type_short_forms.get(leave_type["name"], leave_type["name"]): 0 for leave_type in all_leave_types}

	# Calculate total leave used for each leave type
	for leave_date, leave_type in leave_details.items():
		if "On Leave" in leave_type:
			leave_type = leave_type.split(" - ")[1]
			leave_types[leave_type_short_forms.get(leave_type, leave_type)] += 1

	# Define columns for the report
	columns = [
		{"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150}
	]

	# Create a list of dates within the selected date range
	all_dates = []
	current_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
	end_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")
	while current_date <= end_date:
		all_dates.append(current_date.strftime("%Y-%m-%d"))
		current_date += timedelta(days=1)


	# Add columns for each date within the selected date range
	for date_str in all_dates:
		formatted_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%a %d")
		columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 90})


	columns.extend([
		{"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150}

	])


	
	#     columns.append({"label": f"{leave_type}", "fieldname": leave_type.lower().replace(" ", "_") + "_leave_used", "fieldtype": "Data", "width": 50})
	for leave_type, leave_count in leave_types.items():
		columns.append({"label": f"{leave_type}", "fieldname": leave_type.lower().replace(" ", "_") + "_leave_used", "fieldtype": "Data", "width": 50})

	# Add MO and MI columns for total count
	columns.extend([
		{"label": "MO", "fieldname": "morning_shift_total", "fieldtype": "Data", "width": 50},
		{"label": "MI", "fieldname": "mid_shift_total", "fieldtype": "Data", "width": 50},
		{"label": "MP", "fieldname": "missing_punches_and_absent_total", "fieldtype": "Data", "width": 50},
		{"label": "A", "fieldname": "total_empty_columns", "fieldtype": "Data", "width": 50},
		{"label": "Total", "fieldname": "total_selected_dates", "fieldtype": "Data", "width": 100},
		{"label": "Total Payable Days", "fieldname": "total_payable_days", "fieldtype": "Data", "width": 100},
	])

	# Map statuses to short codes
	status_short_forms = {
		"P": "P",
		"Present": "p",
		"MO": "MO",
		"MI": "MI",
		"Absent": "A",
		"Missing Punches": "MP"
	}

	data = []
	for employee_id, data_row in employee_data.items():
		row = {
			"employee": data_row["employee_id"],
			"employee_name": data_row["employee_name"],
			"department": data_row["department"]
		}
		total_present = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "P" and date_str in all_dates)
		total_leave = sum(1 for date_str, status in data_row["status_by_date"].items() if "On Leave" in status and date_str in all_dates)
		morning_shift_total = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "MO" and date_str in all_dates)
		mid_shift_total = sum(1 for date_str, status in data_row["status_by_date"].items() if status == "MI" and date_str in all_dates)
		missing_punches_and_absent_total = sum(1 for date_str, status in data_row["status_by_date"].items() if status in ["Missing Punches", "Absent"] and date_str in all_dates)

		row["morning_shift_total"] = morning_shift_total
		row["mid_shift_total"] = mid_shift_total
		row["missing_punches_and_absent_total"] = missing_punches_and_absent_total
		row["total_present"] = total_present
		row["total_leave"] = total_leave

		# Add total selected dates count
		total_selected_dates_count = len(all_dates)
		row["total_selected_dates"] = total_selected_dates_count

		# Calculate total empty columns count
		total_empty_columns_count = total_selected_dates_count - len(data_row["status_by_date"])
		row["total_empty_columns"] = total_empty_columns_count

		# Calculate total payable days
		total_payable_days = total_selected_dates_count - missing_punches_and_absent_total
		row["total_payable_days"] = total_payable_days

		# Add leave details for each date within the selected date range
		for date_str in all_dates:
			status = data_row["status_by_date"].get(date_str, "")
			row[date_str] = status_short_forms.get(status, status)

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
	print('/////////////////////////')
	source_data = source_get_data(filters)
	return source_data

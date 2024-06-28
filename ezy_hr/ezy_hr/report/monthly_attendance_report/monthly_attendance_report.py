# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt


import frappe
from datetime import datetime
from frappe.utils import flt, formatdate
from ezy_hr.ezy_hr.report.employee_checkin_and_checkout_details.employee_checkin_and_checkout_details import get_data as source_get_data

def get_leave_dates(filters,employee_id):
	frappe.errprint("Entered into leave_details")
	start_date = filters.get("from_date")
	end_date = filters.get("to_date")
	
	if not start_date or not end_date:
		return {}

	leave_data = frappe.get_all("Leave Application", filters={"employee": employee_id, 
															  "status": "Approved",
															  "from_date": [">=", start_date],
															  "to_date": ["<=", end_date]},
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
	
	# frappe.logger("leave_details", allow_site=True, max_size=25, file_count=25)
	# frappe.errprint(leave_details)
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
	
	all_leave_types = frappe.get_all("Leave Type", fields=["name"])
	leave_type_short_forms = {
		"Week Off": "Wo",
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
	}

	leave_types = {leave_type_short_forms.get(leave_type["name"]): 0 for leave_type in all_leave_types}

	employee_data = {}
	leave_details = None
	is_not_repeat = False
	# Process each entry in the source data
	for entry in source_data:
		employee_id = entry.get("employee")
		employee_name = entry.get("employee_name")
		department = entry.get("department")
		designation = entry.get("designation")
		date_of_joining = entry.get("date_of_joining").formatdate()

		if employee_id:
			if employee_id not in employee_data:
				is_not_repeat = True
				employee_data[employee_id] = {
					"employee_id": employee_id,
					"employee_name": employee_name,
					"department": department,
					"designation":designation,
					"date_of_joining":date_of_joining,
					"status_by_date": {},
					"leaves_details":{leave_type["name"]: 0 for leave_type in all_leave_types}
				}
			else:
				is_not_repeat = False
			
			date = datetime.strptime(entry.get("date"),"%Y-%m-%d").date()
			date_str =  date.strftime("%Y-%m-%d")
			status = entry.get("status")

			if is_not_repeat:
				leave_details = get_leave_dates(filters,employee_id)
			

			employee_data[employee_id]["status_by_date"][date_str] = status
			if is_not_repeat:
				total_leaves = 0
				for dates, leave in leave_details.items():
					leave_date_val = datetime.strptime(dates,"%Y-%m-%d").date()
					str_leave_val = leave_date_val.strftime("%Y-%m-%d")
					employee_data[employee_id]["status_by_date"][str_leave_val] = leave
					if "On Leave" in leave:
						frappe.log_error("On Leave",leave)
						leave_type_value = leave.split(" - ")[1].strip()
						employee_data[employee_id]["leaves_details"][leave_type_value] += 1
						

	# frappe.log_error("final data",employee_data)

	# Define columns for the report
	columns = [
		{"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
		{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
		{"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150},
		{"label": "DOJ", "fieldname": "date_of_joining", "fieldtype": "Data", "width": 150},
	]

	# Create a list of dates within the selected date range
	all_dates = []
	current_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d").date()
	end_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d").date()
	while current_date <= end_date:
		all_dates.append(current_date.strftime("%Y-%m-%d"))
		current_date += timedelta(days=1)


	# Add columns for each date within the selected date range
	for date_str in all_dates:
		formatted_date = datetime.strptime(date_str,"%Y-%m-%d").date().strftime("%a %d")
		columns.append({"label": formatted_date, "fieldname": date_str, "fieldtype": "Data", "width": 90})


	columns.extend([
		{"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100,"hidden":1},
		{"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150,"hidden":1},
		{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150,"hidden":1}

	])


	
	#     columns.append({"label": f"{leave_type}", "fieldname": leave_type.lower().replace(" ", "_") + "_leave_used", "fieldtype": "Data", "width": 50})
	for leave_type, leave_count in leave_types.items():
		columns.append({"label": f"{leave_type}", "fieldname": leave_type, "fieldtype": "Data", "width": 50})

	# Add MO and MI columns for total count
	columns.extend([
		{"label": "MO", "fieldname": "morning_shift_total", "fieldtype": "Data", "width": 50},
		{"label": "MI", "fieldname": "mid_shift_total", "fieldtype": "Data", "width": 50},
		{"label": "MP", "fieldname": "missing_punches_and_absent_total", "fieldtype": "Data", "width": 50},
		{"label": "A", "fieldname": "total_empty_columns", "fieldtype": "Data", "width": 50},
		{"label": "Total Leaves", "fieldname": "total_leave", "fieldtype": "Data", "width": 50},
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
		"Missing Punches": "MP",
		"Sunday":"Week Off"
	}

	total_present = 0
	total_leave = 0
	morning_shift_total= 0
	mid_shift_total = 0
	missing_punches_and_absent_total = 0

	data = []
	for employee_id, data_row in employee_data.items():
		row = {
			"employee": data_row["employee_id"],
			"employee_name": data_row["employee_name"],
			"department": data_row["department"],
			"designation":data_row["designation"],
			"date_of_joining":data_row["date_of_joining"],
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
			status = data_row["status_by_date"].get(date_str, None)
			row[date_str] = status_short_forms.get(status, status)

		for leave_types,count in data_row["leaves_details"].items():
			row[leave_type_short_forms.get(leave_types,leave_types)] = count

		data.append(row)

	# frappe.log_error("final col",columns)
	# frappe.log_error("final data",data)
		
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

# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	columns = [{"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
	{"label": "Txn Type", "fieldname": "txn_type", "fieldtype": "Data", "width": 150},
	{"label": "Credit Account Number", "fieldname": "bank_account_no", "fieldtype": "Data", "width": 150},
	{"label": "Credit Account Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},		
	{"label": "IFSC", "fieldname": "custom_ifsc", "fieldtype": "Data", "width": 150},
	{"label": "Amount", "fieldname": "net_pay", "fieldtype": "Data", "width": 150},
	{"label": "Narration", "fieldname": "narration", "fieldtype": "Data", "width": 150},
	{"label": "Attendance Device Id", "fieldname": "attendance_device_id", "fieldtype": "Data", "width": 150},
	{"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
	{"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150}]

	return columns

def get_data(filters):
	final_data = []
	if filters.employee:
		emp_salary = frappe.db.get_list("Salary Slip",filters= {"start_date":filters.from_date,"end_date":filters.to_date,"company":filters.company,"employee":filters.employee},fields=['employee','company','employee_name','net_pay','bank_name','bank_account_no','custom_ifsc','department','designation'])
	else:
		emp_salary = frappe.db.get_list("Salary Slip",filters= {"start_date":filters.from_date,"end_date":filters.to_date,"company":filters.company},fields=['employee','company','employee_name','net_pay','bank_name','bank_account_no','custom_ifsc','department','designation'])
	# for i in emp_salary:
	# 	print(i)
	# 	final_data.append({
	# 		"employee":i["employee"],
	# 		"employee_name":i["employee_name"],
	# 		"net_pay":i["net_pay"]
	# 	})
	emp_attendace_id = frappe.db.get_list("Employee",['name','attendance_device_id'])

	for i in emp_salary:

		narration = None
		month = filters.get("from_date")
		date_obj = datetime.strptime(month, "%Y-%m-%d")
		formatted_date = date_obj.strftime("%B-%Y")

		narration = f'Salary {formatted_date}'
		i.update({"narration":narration})
		i.update({"txn_type":"NEFT"})
		final_data.append(i)
		for empid in emp_attendace_id:
			if i['employee'] == empid['name']:
				i.update({'attendance_device_id':empid['attendance_device_id']})
	
	return final_data
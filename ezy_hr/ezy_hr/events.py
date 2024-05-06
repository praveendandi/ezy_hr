import frappe
from datetime import datetime

def weekoff_limit_for_month(doc,method=None):
	current_year = datetime.now().year
	current_month = datetime.now().month
	weekoff_leave_data = frappe.db.sql("""
		SELECT employee, leave_type, from_date,total_leave_days
		FROM `tabLeave Application`
		WHERE leave_type = %s AND YEAR(from_date) = %s AND MONTH(from_date) = %s
	""", ("Weekly Off", current_year, current_month), as_dict=True)

	leave_info = {}

	# Count leaves and total_leave_days for each employee
	for emp in weekoff_leave_data:
		emp_id = emp['employee']
		leave_type = emp['leave_type']
		total_leave_days = emp['total_leave_days']
		
		if emp_id not in leave_info:
			print(total_leave_days,"7677777777777")
			leave_info[emp_id] = {'leave_count': 0, 'total_leave_days': 0}

		# If leave type is "Week Off", increment leave count
		if leave_type == "Weekly Off":
			print(total_leave_days,"7677777777777")
			leave_info[emp_id]['leave_count'] += 1
			leave_info[emp_id]['total_leave_days'] += total_leave_days

	# Check if any employee has exceeded the leave limit or total_leave_days
	for emp_id, info in leave_info.items():
		if info['total_leave_days'] > 2:
			frappe.throw(f"Employee {emp_id} has applied for more than 5 week off leaves in the specified month.")
		# if info['total_leave_days'] > 2:
		# 	frappe.throw(f"Employee {emp_id} has total leave days exceeding 2 in the specified month.")

	print(leave_info,";;;;;")
	return leave_info
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
		if info['total_leave_days'] > 5:
			frappe.throw(f"Employee {emp_id} has applied for more than 5 week off leaves in the specified month.")
		# if info['total_leave_days'] > 2:
		# 	frappe.throw(f"Employee {emp_id} has total leave days exceeding 2 in the specified month.")

	print(leave_info,";;;;;")
	return leave_info

from datetime import date
import frappe

def flexi_weekoff():
    try:
        # Retrieve leave types that have the custom flexible week off enabled
        weekoff_leave_types = frappe.db.get_list(
            "Leave Type",
            filters={"custom_flexi_week_off": 1},
            fields=['name', 'custom_unit', 'custom_holiday_list', 'custom_unit_holiday_list', 'custom_select_holiday_type']
        )
        
        if not weekoff_leave_types:
            frappe.log_error(message="No leave types with custom_flexi_week_off found", title="Flexi Weekoff Error")
            return
        
        for weekoff in weekoff_leave_types:
            weekoff_type = weekoff["custom_select_holiday_type"]
            unit_holiday_list = weekoff["custom_unit_holiday_list"]
            
            if not unit_holiday_list:
                frappe.log_error(message=f"No unit holiday list found for {weekoff['name']}", title="Flexi Weekoff Error")
                continue
            
            # Prepare the holiday query based on the type of holiday
            if weekoff_type == "For Week Off":
                holiday_query = """
                    SELECT holiday_date, description
                    FROM `tabHoliday`
                    WHERE parent = %s AND parentfield = 'holidays' AND parenttype = 'Holiday List' AND weekly_off = 1
                """
            elif weekoff_type == "For Public Holiday":
                holiday_query = """
                    SELECT holiday_date, description
                    FROM `tabHoliday`
                    WHERE parent = %s AND parentfield = 'holidays' AND parenttype = 'Holiday List' AND weekly_off = 0
                """
            else:
                frappe.log_error(message=f"Invalid holiday type for {weekoff['name']}", title="Flexi Weekoff Error")
                continue
            
            holiday_dates = frappe.db.sql(holiday_query, unit_holiday_list, as_dict=True)
            
            today = date.today()
            for holiday in holiday_dates:
                if today == holiday['holiday_date']:
                    date_and_description = f"{holiday['holiday_date']},{holiday['description']}"
                    
                    employee_ids = frappe.db.get_list(
                        "Employee",
                        filters={"company": weekoff["custom_unit"], "holiday_list": weekoff["custom_holiday_list"]},
                        fields=["name"]
                    )

                    for emp in employee_ids:
                        leave_allocations = frappe.db.get_list(
                            "Leave Allocation",
                            filters={"employee": emp["name"], "leave_type": weekoff["name"]},
                            fields=["name", "total_leaves_allocated", "new_leaves_allocated", "custom_leave_allocation_date_and_description"]
                        )

                        for allocation in leave_allocations:
                            # Update Leave Allocation with the current holiday information
                            frappe.db.set_value(
                                "Leave Allocation",
                                allocation["name"],
                                "custom_leave_allocation_date_and_description",
                                date_and_description
                            )
                            update_leave_allocation(allocation, date_and_description)

    except Exception as e:
        frappe.log_error(message=str(e), title="Error in flexi_weekoff function")
        print(f"Error in flexi_weekoff function: {str(e)}")

def update_leave_allocation(allocation, date_and_description):
    try:
        leave_allocation_doc = frappe.get_doc("Leave Allocation", allocation['name'])
        leave_allocation_doc.new_leaves_allocated += 1
        leave_allocation_doc.save()
        
        if leave_allocation_doc.docstatus == 1:
            leave_allocation_doc.submit()

        # Create or update Leave Ledger Entry with the current holiday information
        leave_ledger_entry_name = frappe.db.get_value("Leave Ledger Entry", {"transaction_name": leave_allocation_doc.name}, "name")
        
        if leave_ledger_entry_name:
            frappe.db.set_value("Leave Ledger Entry", leave_ledger_entry_name, "custom_reason_date_", date_and_description)
        else:
            new_leave_ledger_entry = frappe.get_doc({
                "doctype": "Leave Ledger Entry",
                "transaction_name": leave_allocation_doc.name,
                "custom_reason_date_": date_and_description,
                "leave_type": leave_allocation_doc.leave_type,
                "employee": leave_allocation_doc.employee
            })
            new_leave_ledger_entry.insert()
            new_leave_ledger_entry.submit()

        print(f"Updated leave allocation: {allocation['name']}, new leaves allocated: {leave_allocation_doc.new_leaves_allocated}")
    except Exception as e:
        frappe.log_error(message=str(e), title="Error updating leave allocation")
        print(f"Error updating leave allocation: {allocation['name']} - {str(e)}")

# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from datetime import datetime

def execute(filters=None):
    try:
        columns, data = [], []
        columns = get_columns(filters)
        data = get_data(filters)
        return columns, data
    
    except Exception as e:
        frappe.log_error(str(e))
    

def get_columns(filters):
    from_date_str = filters.get("from_date")
    to_date_str = filters.get("to_date")

    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date_str, '%Y-%m-%d') if from_date_str else None
    to_date = datetime.strptime(to_date_str, '%Y-%m-%d') if to_date_str else None

    # Format the date labels
    from_date_label = from_date.strftime('%d-%m-%Y') if from_date else ''
    to_date_label = to_date.strftime('%d-%m-%Y') if to_date else ''
    
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data","width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 120},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 120},
        {"label": "Date of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 120},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 120},
        {"label": f"Leave Opening Balance as on {from_date_label}", "fieldname": "leave_opening_balance", "fieldtype": "Float", "width": 320},
        {"label": f"Total Leaves Earned from {from_date_label} to {to_date_label}", "fieldname": "leave_earned", "fieldtype": "Float", "width": 280},
        {"label": f"Leave Availed from {from_date_label} to {to_date_label}", "fieldname": "leave_availed", "fieldtype": "Float", "width": 280},
        {"label": f"Closing Balance as on {to_date_label}", "fieldname": "closing_balance", "fieldtype": "Float", "width": 280},
        {"label": f"Total Present Days B/W {from_date_label} to {to_date_label}", "fieldname": "present_days", "fieldtype": "Int", "width": 300},
    ]
    return columns

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    employee = filters.get("employee")
    leave_type = filters.get("leave_type")

    filter_conditions = {
    }
    
    if employee:
        filter_conditions["employee"] = employee
    if leave_type:
        filter_conditions["leave_type"] = leave_type
        
    if filters.get("company"):
        filter_conditions["unit"] = filters.get("company")

    results = frappe.get_all(
        "Employee Leave Balance",
        filters=filter_conditions,
        fields=[
            "employee", "employee_name", "leave_balance_on", "leave_balance", 
            "leave_balance_updated", "current_leave_balance","leave_type"
        ]
    )

    data = []
    for row in results:
        
        employee_doc = frappe.get_doc("Employee", row.employee)
        department = employee_doc.department if employee_doc else ""
        designation = employee_doc.designation if employee_doc else ""
        date_of_joining = employee_doc.date_of_joining if employee_doc else ""
                
        leave_earned = calculate_leave_earned(row,date_of_joining, filters)
        
        data.append({
            "employee": row.employee,
            "employee_name": row.employee_name,
            "department": department,
            "designation": designation,
            "date_of_joining": date_of_joining,
            "leave_opening_balance": row.leave_balance,
        })
        
        if row.get("leave_type") == "Casual Leave":
            leave_availed = leave_used_between_from_to(filters,row,row.get("leave_type"))
            leave_earned_casual =  leave_earned.get('casual_leaves',0)
            value = data[-1]
            clb = closing_balance_details(row,leave_earned_casual,leave_availed)
            
            value.update({
				"leave_earned":leave_earned_casual,
				'leave_availed':leave_availed.get("count",0) if leave_availed else 0,
				'leave_type':row.get("leave_type"),
				'closing_balance':clb
			})
        elif row.get("leave_type") == "Sick Leave":
            leave_availed = leave_used_between_from_to(filters, row,row.get("leave_type"))
            leave_earned_sick = leave_earned.get('sick_leaves',0)
            value = data[-1]
            clb = closing_balance_details(row,leave_earned_sick,leave_availed)
            value.update({
				"leave_earned":leave_earned_sick,
				'leave_availed':leave_availed.get("count",0) if leave_availed else 0,
    			'leave_type':row.get("leave_type"),
       			'closing_balance':clb
			})
            
        elif row.get("leave_type") == "Privilege Leave":
            leave_availed = leave_used_between_from_to(filters, row,row.get("leave_type"))
            leave_earned_privilege = leave_earned.get("privilege_leaves",0)
            value = data[-1]
            clb = closing_balance_details(row,leave_earned_privilege,leave_availed)
            
            value.update({
				"leave_earned":leave_earned_privilege,
				'leave_availed':leave_availed.get("count",0) if leave_availed else 0,
				'leave_type':row.get("leave_type"),
				'closing_balance':clb
			})
            
            
        present_days = calculate_present_days(row, filters)
        value = data[-1]
        value.update({
			"present_days":present_days,
   		})
        
    
    return data

def closing_balance_details(row,leave_earned,leave_availed):
    
    closing_balance = (
		(row.leave_balance + leave_earned) - (leave_availed.get("count",0) if leave_availed else 0)
    )
    return closing_balance
    
def leave_used_between_from_to(filters,row,leave_type):
    filter_conditions = []
    filter_values = []

    filter_conditions.append("from_date BETWEEN %s AND %s")
    filter_values.append(filters.get("from_date"))
    filter_values.append(filters.get("to_date"))

    if row.get("employee"):
        filter_conditions.append("employee = %s")
        filter_values.append(row.get("employee"))

    if leave_type:
        filter_conditions.append("leave_type = %s")
        filter_values.append(leave_type)

    where_clause = " AND ".join(filter_conditions)

    results = frappe.db.sql(
        f"""
        SELECT SUM(total_leave_days) AS count, leave_type
        FROM `tabLeave Application`
        WHERE {where_clause} AND docstatus = 1
        GROUP BY leave_type
        """,
        filter_values,
        as_dict=True
    )
    
    if len(results) >0:
        return results[0]

    return 0
 
def calculate_leave_earned(row, date_of_joining,filters):
    
    leave_balance_on = row.leave_balance_on  # Assuming it's a date object
    alloction_date_start = None
    # Convert to datetime if necessary
    
    from_date = datetime.strptime(filters.get("from_date"), '%Y-%m-%d').date()
    to_date = datetime.strptime(filters.get("to_date"), '%Y-%m-%d').date()
    
        
    if leave_balance_on >= date_of_joining <= to_date:
        alloction_date_start = leave_balance_on
    else:
        alloction_date_start = leave_balance_on

    # Calculate months between start_date and to_date
    months = (to_date.year - alloction_date_start.year) * 12 + (to_date.month - alloction_date_start.month)
    
    # Monthly allocation of leaves
    casual_leaves_per_month = 1
    sick_leaves_per_month = 1
    
    # Total Casual and Sick Leaves earned
    casual_leaves_earned = months * casual_leaves_per_month
    sick_leaves_earned = months * sick_leaves_per_month
    
    # Calculate Privilege Leave based on Present Days
    present_days = calculate_present_days(row, filters)  # Implement this function
    
    if present_days >=25:
        months__privilege = (to_date.year - alloction_date_start.year) * 12 + (to_date.month - alloction_date_start.month)
        privilege_leaves_earned = flt(months__privilege  * 1.5)
    else:
        privilege_leaves_earned = 0
    
    print({
        "casual_leaves": casual_leaves_earned,
        "sick_leaves": sick_leaves_earned,
        "privilege_leaves": privilege_leaves_earned
    })
    
    return {
        "casual_leaves": casual_leaves_earned,
        "sick_leaves": sick_leaves_earned,
        "privilege_leaves": privilege_leaves_earned
    }
   
def calculate_present_days(row, filters):
    # Implement logic to calculate total present days between from_date and to_date
    filter_conditions = []
    filter_values = []

    filter_conditions.append("attendance_date BETWEEN %s AND %s")
    filter_values.append(filters.get("from_date"))
    filter_values.append(filters.get("to_date"))

    if row.get("employee"):
        filter_conditions.append("employee = %s")
        filter_values.append(row.get("employee"))
        
    filter_conditions.append("status = %s")
    filter_values.append('Present')

    where_clause = " AND ".join(filter_conditions)
    
    results = frappe.db.sql(
        f"""
        SELECT Count(name) AS count
        FROM `tabAttendance`
        WHERE {where_clause} AND docstatus = 1
        GROUP BY status
        """,
        filter_values,
        as_dict=1
    )
   
    if len(results)>0:
        return results[0].get("count")

    return 0


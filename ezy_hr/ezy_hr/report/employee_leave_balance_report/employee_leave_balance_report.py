# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if filters is None:
        filters = {}

    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        # {"label": "Leave Balance Given On", "fieldname": "leave_balance_on", "fieldtype": "Date", "width": 200},
        # {"label": "Leave Balance Updated On", "fieldname": "leave_balance_updated", "fieldtype": "Date", "width": 210},
    ]

    leave_type_abbr = {
        "Casual Leave": "CL",
        "Privilege Leave": "PL",
        "Paternity Leave": "PTL",
        "Sick Leave": "SL",
        "Flexi Saturday": "FS",
        "Flexi Public Holiday": "FPH",
        "Flexi Week Off": "FWO",
        "Compensatory Off (COL)": "COL",
        "Holiday": "HO",
        "Week Off": "WO",
        "Maternity Leave": "ML",
        "Accident Leave on shift": "ALS",
        "ESI Leave": "ESI",
        "Unpaid Leave": "UL",
        "Leave Without Pay": "LWP",
        "Compensatory Off": "CO"
    }

    leave_types = []
    if filters.get("leave_type"):
        leave_types = [{"leave_type": filters.get("leave_type")}]
    else:
        leave_types = frappe.get_all("Employee Leave Balance", fields=["distinct leave_type"])
    
    leave_types_list = [lt['leave_type'] for lt in leave_types]
    
    employee_filters = {"status": "Active"}
    if filters.get("unit"):
        employee_filters["company"] = filters.get("unit")
    if filters.get("employee"):
        employee_filters["name"] = ["in", filters.get("employee")]

    active_employees = frappe.get_all(
        "Employee",
        filters=employee_filters,
        fields=["name"]
    )
    active_employee_list = [emp['name'] for emp in active_employees]
    
    if not active_employee_list:
        frappe.throw(_("No active employees found for the selected unit (company)"))

    for leave_type in leave_types_list:
        abbr = leave_type_abbr.get(leave_type, leave_type[:2])
        columns.extend([
            {"label": f"{abbr} Opening Balance", "fieldname": f"{abbr.lower()}_leave_balance", "fieldtype": "Float", "width": 180},
            # {"label": f"{abbr} Allocated Frequency", "fieldname": f"{abbr.lower()}_allocate_frequency", "fieldtype": "Data", "width": 200},
            # {"label": f"{abbr} Allocated Count", "fieldname": f"{abbr.lower()}_allocated_count", "fieldtype": "Float", "width": 180},
            {"label": f"{abbr} Updated Balance", "fieldname": f"{abbr.lower()}_current_leave_balance", "fieldtype": "Float", "width": 180},
            {"label": f"{abbr} Used Leaves", "fieldname": f"{abbr.lower()}_used_leaves", "fieldtype": "Float", "width": 180},
            {"label": f"{abbr} Current Balance", "fieldname": f"{abbr.lower()}_adjusted_balance", "fieldtype": "Float", "width": 180}
        ])

    leave_balances_filters = {
        "employee": ["in", active_employee_list],
    }
    if filters.get("leave_type"):
        leave_balances_filters["leave_type"] = filters.get("leave_type")

    leave_balances = frappe.get_all(
        "Employee Leave Balance",
        filters=leave_balances_filters,
        fields=["employee", "employee_name", "leave_type", "leave_balance_on", "allocate_frequency", "allocated_count", "leave_balance_updated", "leave_balance", "current_leave_balance"],
        order_by="employee, leave_balance_on"
    )

    used_leaves_filters = {
        "status": "Approved",
    }
    if filters.get("leave_type"):
        used_leaves_filters["leave_type"] = filters.get("leave_type")
    if filters.get("employee"):
        used_leaves_filters["employee"] = ["in", filters.get("employee")]
    
    used_leaves_data = frappe.get_all(
        "Leave Application",
        filters=used_leaves_filters,
        fields=["employee", "leave_type", "sum(total_leave_days) as used_leaves"],
        group_by="employee, leave_type"
    )
    
    used_leaves_map = {(row['employee'], row['leave_type']): row['used_leaves'] for row in used_leaves_data}
    
    employee_data = {}

    for leave in leave_balances:
        emp_key = leave['employee']
        leave_type = leave['leave_type']
        abbr = leave_type_abbr.get(leave_type, leave_type[:2]).lower()

        if emp_key not in employee_data:
            employee_data[emp_key] = {
                "employee": leave["employee"],
                "employee_name": leave["employee_name"],
                "leave_balance_on": leave["leave_balance_on"],
                "allocate_frequency": leave["allocate_frequency"],
                "allocated_count": leave["allocated_count"],
                "leave_balance_updated": leave["leave_balance_updated"],
            }

        employee_data[emp_key][f"{abbr}_leave_balance"] = leave.get("leave_balance", 0)
        employee_data[emp_key][f"{abbr}_allocate_frequency"] = leave.get("allocate_frequency", "N/A")  # Default value if not available
        employee_data[emp_key][f"{abbr}_allocated_count"] = leave.get("allocated_count", 0)
        employee_data[emp_key][f"{abbr}_current_leave_balance"] = leave.get("current_leave_balance", 0)
        employee_data[emp_key][f"{abbr}_used_leaves"] = used_leaves_map.get((leave["employee"], leave["leave_type"]), 0)
        adjusted_balance = employee_data[emp_key][f"{abbr}_current_leave_balance"] - employee_data[emp_key][f"{abbr}_used_leaves"]
        employee_data[emp_key][f"{abbr}_adjusted_balance"] = adjusted_balance

    data = list(employee_data.values())

    return columns, data

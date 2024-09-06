# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
def execute(filters=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        # {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 150},
        {"label": "Leave Balance Given On", "fieldname": "leave_balance_on", "fieldtype": "Date", "width": 200},
        {"label": "Allocate Frequency", "fieldname": "allocate_frequency", "fieldtype": "Data", "width": 150},
        {"label": "Allocated Count", "fieldname": "allocated_count", "fieldtype": "Float", "width": 150},
        {"label": "Leaves Updated On", "fieldname": "leave_balance_updated", "fieldtype": "Date", "width": 180}
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
        "ESI Leave" : "ESI",
        "Unpaid Leave" : "UL",
        "Leave Without Pay" : "LWP",
        "Compensatory Off" : "CO"
    }

    leave_types = frappe.get_all("Employee Leave Balance", fields=["employee", "employee_name", "leave_type", "leave_balance_on", "allocate_frequency", "allocated_count", "leave_balance_updated"])

    leave_type_filters = []
    if filters.get("leave_type"):
        leave_type_filters.append(filters.get("leave_type"))
    else:
        leave_type_filters = [leave['leave_type'] for leave in leave_types]

    added_leave_types = set()

    for leave_type in leave_type_filters:
        abbr = leave_type_abbr.get(leave_type, leave_type[:2])
        if abbr not in added_leave_types:
            columns.append({"label": f"{abbr} Opening Balance", "fieldname": f"{abbr.lower()}_leave_balance", "fieldtype": "Float", "width": 180})
            columns.append({"label": f"{abbr} Total Balance", "fieldname": f"{abbr.lower()}_current_balance", "fieldtype": "Float", "width": 180})
            columns.append({"label": f"{abbr} Used Leaves", "fieldname": f"{abbr.lower()}_used_leaves", "fieldtype": "Float", "width": 180})
            columns.append({"label": f"{abbr} Current Balance", "fieldname": f"{abbr.lower()}_adjusted_balance", "fieldtype": "Float", "width": 180})
            added_leave_types.add(abbr)  

    conditions = {}
    if filters.get("unit"):
        conditions["unit"] = filters.get("unit")
    if filters.get("employee"):
        conditions["employee"] = filters.get("employee")
    if filters.get("leave_type"):
        conditions["leave_type"] = filters.get("leave_type")

    leave_balances = frappe.get_all(
        "Employee Leave Balance",
        filters=conditions,
        fields=["employee", "employee_name", "leave_type", "allocate_frequency", "allocated_count",
                "leave_balance_on", "leave_balance", "leave_balance_updated", "current_leave_balance"],
        order_by="employee, leave_balance_on"
    )

    used_leaves_data = frappe.get_all(
        "Leave Application",
        filters={"status": "Approved"},
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
                "leave_type": leave["leave_type"],  # Add leave_type here
                "leave_balance_on": leave["leave_balance_on"],
                "allocate_frequency": leave["allocate_frequency"],
                "allocated_count": leave["allocated_count"],
                "leave_balance_updated": leave["leave_balance_updated"],
            }

        employee_data[emp_key][f"{abbr}_leave_balance"] = leave["leave_balance"]
        employee_data[emp_key][f"{abbr}_current_balance"] = leave["current_leave_balance"]
        employee_data[emp_key][f"{abbr}_used_leaves"] = used_leaves_map.get((leave["employee"], leave["leave_type"]), 0)
        adjusted_balance = leave["current_leave_balance"] - employee_data[emp_key][f"{abbr}_used_leaves"]
        employee_data[emp_key][f"{abbr}_adjusted_balance"] = adjusted_balance

    data = list(employee_data.values())

    return columns, data

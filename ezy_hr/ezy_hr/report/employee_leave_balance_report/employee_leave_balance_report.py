# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Data", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Link", "options": "Leave Type", "width": 150},
        {"label": "Leave Balance Given On", "fieldname": "leave_balance_on", "fieldtype": "Date", "width": 200},
        {"label": "Allocate Frequency", "fieldname": "allocate_frequency", "fieldtype": "Data", "width": 150},
        {"label": "Allocated Count", "fieldname": "allocated_count", "fieldtype": "Float", "width": 150},
        {"label": "Leaves Updated On", "fieldname": "leave_balance_updated", "fieldtype": "Date", "width": 180},
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

    leave_types = []
    if filters.get("leave_type"):
        leave_types = [{"leave_type": filters.get("leave_type")}]
    else:
        leave_types = frappe.get_all("Employee Leave Balance", fields=["distinct leave_type"])

    for leave_type in leave_types:
        leave_type_name = leave_type['leave_type']
        abbr = leave_type_abbr.get(leave_type_name, leave_type_name[:2]) 
        columns.append({"label": f"{abbr} Opening Balance", "fieldname": f"{abbr.lower()}_leave_balance", "fieldtype": "Float", "width": 180})
        columns.append({"label": f"{abbr} Current Balance", "fieldname": f"{abbr.lower()}_current_balance", "fieldtype": "Float", "width": 180})

    conditions = {}
    if filters.get("unit"):
        conditions["unit"] = filters.get("unit")
    if filters.get("employee"):
        conditions["employee"] = filters.get("employee")
    if filters.get("employee_name"):
        conditions["employee_name"] = ['like', '%' + filters.get("employee_name") + '%']
    if filters.get("leave_type"):
        conditions["leave_type"] = filters.get("leave_type")
    
    leave_balances = frappe.get_all(
        "Employee Leave Balance",
        filters=conditions,
        fields=["employee", "employee_name", "leave_type", "allocate_frequency", "allocated_count",
                "leave_balance_on", "leave_balance", "leave_balance_updated", "current_leave_balance"],
        order_by="employee, leave_balance_on"
    )

    data_dict = {}

    for leave in leave_balances:
        key = (leave['employee'], leave['leave_balance_on'])
        leave_type = leave['leave_type']
        abbr = leave_type_abbr.get(leave_type, leave_type[:2]).lower()  

        if key not in data_dict:
            data_dict[key] = {
                "employee": leave["employee"],
                "employee_name": leave["employee_name"],
                "leave_type": leave["leave_type"],  
                "leave_balance_on": leave["leave_balance_on"],
                "allocate_frequency": leave["allocate_frequency"],
                "allocated_count": leave["allocated_count"],
                "leave_balance": leave["leave_balance"],
                "leave_balance_updated": leave["leave_balance_updated"],
                "current_leave_balance": leave["current_leave_balance"]
            }

        data_dict[key][f"{abbr}_leave_balance"] = leave["leave_balance"]
        data_dict[key][f"{abbr}_current_balance"] = leave["current_leave_balance"]

    data = list(data_dict.values())

    return columns, data

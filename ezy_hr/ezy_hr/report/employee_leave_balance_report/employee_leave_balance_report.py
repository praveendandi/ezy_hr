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
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 120},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 120},
        {"label": "Date of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 120},
        {"label": "Leave Type", "fieldname": "leave_type", "fieldtype": "Data", "width": 120},
    ]

    dynamic_columns_added = False

    leave_type_abbr = {
        "Casual Leave": "CL",
        "Privilege Leave": "PL",
        "Sick Leave": "SL",
        # Add all other leave types here...
    }

    leave_allocations_per_month = {
        "Privilege Leave": 1.5,
        "Casual Leave": 1,
        "Sick Leave": 1,
    }

    employee_filters = {"status": "Active"}

    if filters.get("unit"):
        employee_filters["company"] = filters.get("unit")

    if filters.get("employee"):
        employee_filters["name"] = filters.get("employee")

    employees = frappe.get_all(
        "Employee",
        filters=employee_filters,
        fields=["name", "employee_name", "department", "designation", "date_of_joining"]
    )

    leave_balances = frappe.get_all(
        "Employee Leave Balance",
        filters={"leave_type": filters.get("leave_type")} if filters.get("leave_type") else {},
        fields=["employee", "leave_type", "leave_balance", "current_leave_balance", "leave_balance_on", "leave_balance_updated", "allocated_count"]
    )

    used_leaves_data = frappe.get_all(
        "Leave Application",
        filters={"status": "Approved"},
        fields=["employee", "leave_type", "sum(total_leave_days) as used_leaves"],
        group_by="employee, leave_type"
    )

    attendance_data = frappe.get_all(
        "Attendance",
        filters={"status": "Present"},
        fields=["employee", "count(name) as present_days"],
        group_by="employee"
    )

    # Create a dictionary for used leaves and attendance for easy lookup
    used_leaves_map = {(row['employee'], row['leave_type']): row['used_leaves'] for row in used_leaves_data}
    attendance_map = {row['employee']: row['present_days'] for row in attendance_data}

    data = []

    for employee in employees:
        emp_key = employee["name"]

        employee_leaves = [leave for leave in leave_balances if leave["employee"] == emp_key]

        for leave in employee_leaves:
            leave_type = leave["leave_type"]
            leave_balance_on_date = leave.get("leave_balance_on", "")
            leave_balance_updated = leave.get("leave_balance_updated", "")

            if leave_balance_on_date and leave_balance_updated:
                months_between = (leave_balance_updated.year - leave_balance_on_date.year) * 12 + (leave_balance_updated.month - leave_balance_on_date.month)
            else:
                months_between = 0

            allocated_per_month = leave_allocations_per_month.get(leave_type, 0)
            leave_earned = allocated_per_month * months_between if months_between > 0 else 0

            leave_earned_start = leave_balance_on_date.strftime("%b-%y") if leave_balance_on_date else ""
            leave_earned_end = leave_balance_updated.strftime("%b-%y") if leave_balance_updated else ""
            closing_balance_date = leave_balance_updated.strftime("%d-%m-%Y") if leave_balance_updated else ""

            if not dynamic_columns_added:
                columns.extend([
                                        {
                            "label": f"Leave Opening Balance as on \n{leave_balance_on_date.strftime('%d-%m-%Y') if leave_balance_on_date else ''}",
                            "fieldname": "leave_opening_balance", 
                            "fieldtype": "Float", 
                            "width": 280
                        },

                    {"label": f"Leave Earned from {leave_earned_start} to {leave_earned_end}",
                     "fieldname": "leave_earned", "fieldtype": "Float", "width": 280},
                    {"label": f"Leave Availed from {leave_earned_start} to {leave_earned_end}",
                     "fieldname": "leave_availed", "fieldtype": "Float", "width": 280},
                    {"label": f"Closing Balance as on {closing_balance_date}",
                     "fieldname": "closing_balance", "fieldtype": "Float", "width": 280},
                    {"label": f"Total Present Days B/W {leave_earned_start} to {leave_earned_end}", "fieldname": "present_days", "fieldtype": "Int", "width": 300},
                    {"label": "Total Leave Days", "fieldname": "on_leave_days", "fieldtype": "Int", "width": 280},
                ])
                dynamic_columns_added = True

            opening_balance = leave.get("leave_balance", 0)
            availed = used_leaves_map.get((emp_key, leave_type), 0)
            closing_balance = leave.get("current_leave_balance", 0)
            adjusted_balance = closing_balance - availed

            present_days = attendance_map.get(emp_key, 0)
            on_leave_days = availed

            data.append({
                "employee": employee["name"],
                "employee_name": employee["employee_name"],
                "department": employee.get("department", ""),
                "designation": employee.get("designation", ""),
                "date_of_joining": employee.get("date_of_joining", ""),
                "leave_type": leave_type,
                "leave_opening_balance": opening_balance,
                "leave_earned": leave_earned,
                "leave_availed": availed,
                "closing_balance": adjusted_balance,
                "present_days": present_days,
                "on_leave_days": on_leave_days
            })

    return columns, data

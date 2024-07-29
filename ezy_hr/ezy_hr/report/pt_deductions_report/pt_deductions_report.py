# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
 
# from hrms.payroll.report.provident_fund_deductions.provident_fund_deductions import get_conditions
 
 
def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters) if len(data) else []
 
    return columns, data
 
 
def get_columns(filters):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 200,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "width": 160,
        },
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
    ]
 
    return columns

def get_conditions(filters):
    conditions = ["1=1"]

    if filters.get("department"):
        conditions.append("sal.department = '%s'" % filters["department"])

    if filters.get("company"):
        conditions.append("sal.company = '%s'" % filters["company"])

    if filters.get("from_date"):
        conditions.append("sal.start_date >= '%s'" % filters["from_date"])

    if filters.get("to_date"):
        conditions.append("sal.end_date <= '%s'" % filters["to_date"])

    if filters.get("employee"):
        conditions.append("sal.employee = '%s'" % filters["employee"])


    return " AND ".join(conditions)
 
 
def get_data(filters):
    data = []
 
    component_type_dict = frappe._dict(
        frappe.db.sql(
            """ select name, component_type from `tabSalary Component`
        where component_type = 'Professional Tax' """
        )
    )
 
    if not len(component_type_dict):
        return []
 
    conditions = get_conditions(filters)
 
    # nosemgrep: frappe-semgrep-rules.rules.frappe-using-db-sql
    entry = frappe.db.sql(
        f"""SELECT sal.employee, sal.employee_name, ded.salary_component, ded.amount
        FROM `tabSalary Slip` sal, `tabSalary Detail` ded
        WHERE sal.name = ded.parent
        AND ded.parentfield = 'deductions'
        AND ded.parenttype = 'Salary Slip'
        AND sal.docstatus = 1
        AND {conditions}
        AND ded.salary_component IN ({", ".join(["%s"] * len(component_type_dict))})""",
        tuple(component_type_dict.keys()),
        as_dict=1,
    )
    for d in entry:
        employee = {"employee": d.employee, "employee_name": d.employee_name, "amount": d.amount}
 
        data.append(employee)
 
    return data
 
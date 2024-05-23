# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    try:
        data = get_data(filters)
        columns = get_columns(filters) if len(data) else []

        return columns, data
    except Exception as e:
        frappe.log_error("Professional Tax report",str(e))
        


def get_columns(filters):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Data",
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
	conditions = [""]

	if filters.get("department"):
		conditions.append("sal.department = '%s' " % (filters["department"]))

	if filters.get("branch"):
		conditions.append("sal.branch = '%s' " % (filters["branch"]))

	if filters.get("company"):
		conditions.append("sal.company = '%s' " % (filters["company"]))

	if filters.get("from_date"):
		conditions.append("sal.start_date = '%s' " % (filters["from_date"]))

	if filters.get("to_date"):
		conditions.append("sal.end_date = '%s' " % (filters["to_date"]))

	if filters.get("mode_of_payment"):
		conditions.append("sal.mode_of_payment = '%s' " % (filters["mode_of_payment"]))

	return " and ".join(conditions)

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

    entry = frappe.db.sql(
        """ select sal.employee, sal.employee_name, ded.salary_component, ded.amount
        from `tabSalary Slip` sal, `tabSalary Detail` ded
        where sal.name = ded.parent
        and ded.parentfield = 'deductions'
        and ded.parenttype = 'Salary Slip'
        and sal.docstatus = 1 %s
        and ded.salary_component in (%s)
    """
        % (conditions, ", ".join(["%s"] * len(component_type_dict))),
        tuple(component_type_dict.keys()),
        as_dict=1,
    )


    for d in entry:
        employee = {"employee": d.employee, "employee_name": d.employee_name, "amount": d.amount}
        data.append(employee)

    return data


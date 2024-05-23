# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate

def execute(filters=None):
    try:
        data = get_data(filters)
        
        columns = get_columns(filters) if len(data) else []
        
        return columns, data
    
    except Exception as e:
        frappe.log_error("EPFO Report",str(e))

def get_columns(filters):
    columns = [
        {
            "label": _("EMP Code"),
            "fieldname": "employee",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("UAN"),
            "fieldname": "pf_account",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Member Name"),
            "fieldname": "employee_name",
            "width": 200,
        },
        {
            "label": _("Gross Wages"),
            "fieldname": "gross_amount",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EPF Wages"),
            "fieldname": "epf_wages",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EPS Wages"),
            "fieldname": "eps_wages",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EDLI Wages"),
            "fieldname": "edli_wages",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EPF Contri Remitted"),
            "fieldname": "epf_contri_remitted",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EPS Contri Remitted"),
            "fieldname": "eps_contri_remitted",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EPF EPS Diff Remitted"),
            "fieldname": "epf_eps_diff_remitted",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("NCP Days"),
            "fieldname": "ncp_days",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Refund Of Advances"),
            "fieldname": "refund_of_advances",
            "fieldtype": "Currency",
            "width": 200
        },
		{
            "label": _("Working Days"),
            "fieldname": "total_working_days",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Admin"),
            "fieldname": "admin",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("EDLI Admin"),
            "fieldname": "edli_admin",
            "fieldtype": "Currency",
            "width": 200
        },
        {
            "label": _("Total Contribution"),
            "fieldname": "total_contribution",
            "fieldtype": "Currency",
            "width": 200
        },
    ]
    
    return columns

def get_conditions(filters):
    conditions = ["1=1"]

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

    if filters.get("employee"):
        conditions.append("sal.employee = '%s' " % (filters["employee"]))

    if filters.get("mode_of_payment"):
        conditions.append("sal.mode_of_payment = '%s' " % (filters["mode_of_payment"]))

    return " and ".join(conditions)

def prepare_data(entry, component_type_dict):
    data_list = {}

    employee_account_dict = frappe._dict(
        (employee.name, {"provident_fund_account": employee.provident_fund_account, "custom_gross_amount": employee.custom_gross_amount})
        for employee in frappe.db.sql(
            """SELECT name, provident_fund_account, custom_gross_amount FROM `tabEmployee`""",
            as_dict=True,
        )
    )

    for d in entry:
        component_type = component_type_dict.get(d.salary_component)
        if data_list.get(d.name):
            data_list[d.name][component_type] = d.amount
        else:
            data_list.setdefault(
                d.name,
                {
                    "employee": d.employee,
                    "employee_name": d.employee_name,
                    "pf_account": employee_account_dict.get(d.employee, {}).get("provident_fund_account"),
                    component_type: d.amount,
                    "gross_amount": employee_account_dict.get(d.employee, {}).get("custom_gross_amount"),
                    "total_working_days" : d.total_working_days,
                },
            )
    return data_list

def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    salary_slips = frappe.db.sql(
        """SELECT sal.name FROM `tabSalary Slip` sal
        WHERE docstatus = 1 AND {conditions}
        """.format(conditions=conditions),
        as_dict=1,
    )

    component_type_dict = frappe._dict(
        frappe.db.sql(
            """SELECT name, component_type FROM `tabSalary Component`
            WHERE component_type IN ('Provident Fund', 'Provident Fund Account')"""
        )
    )

    if not len(component_type_dict):
        return []

    entry = frappe.db.sql(
        """SELECT sal.name, sal.employee, sal.employee_name, sal.total_working_days, ded.salary_component, ded.amount
        FROM `tabSalary Slip` sal, `tabSalary Detail` ded
        WHERE sal.name = ded.parent
        AND ded.parentfield = 'deductions'
        AND ded.parenttype = 'Salary Slip'
        AND sal.docstatus = 1
        AND {conditions}
        AND ded.salary_component IN (%s)
        """.format(conditions=conditions) % (", ".join(["%s"] * len(component_type_dict))),
        tuple(component_type_dict.keys()),
        as_dict=1,
    )

    data_list = prepare_data(entry, component_type_dict)

    for d in salary_slips:
        if data_list.get(d.name):
            employee = {
                "employee": data_list.get(d.name).get("employee"),
                "employee_name": data_list.get(d.name).get("employee_name"),
                "total_working_days" : data_list.get(d.name).get("total_working_days"),
                "pf_account": data_list.get(d.name).get("pf_account"),
                "gross_amount": data_list[d.name].get("gross_amount"),
            }

            # Fetch earnings data to calculate EPF, EPS, and EDLI wages
            earning_data = frappe.db.sql(
                """SELECT sal.name, ear.salary_component, ear.amount, ear.abbr
                FROM `tabSalary Slip` sal, `tabSalary Detail` ear
                WHERE sal.name = ear.parent
                AND ear.parentfield = 'earnings'
                AND ear.parenttype = 'Salary Slip'
                AND sal.docstatus = 1
                AND ear.parent=%s
                """, (d.name,),
                as_dict=1,
            )

            basic = 0
            da = 0
            hra = 0

            for i in earning_data:
                if i.abbr == "B":
                    basic = i.amount
                if i.abbr == "DA":
                    da = i.amount
                if i.abbr == "HRA":
                    hra = i.amount

            epf_wages = round(basic + da)
            gross_pay = employee["gross_amount"]
            eps_wages = round((epf_wages * 8.33) / 100)
            edli_wages = round((epf_wages * 0.5) / 100)
            
            epf_contri_remitted = round(epf_wages * 0.12)
            eps_contri_remitted = round(eps_wages * 0.13)
            epf_eps_diff_remitted = round(epf_contri_remitted - eps_contri_remitted)
            admin = round((epf_wages * 0.5) / 100)
            edli_admin = round((edli_wages * 0.5) / 100)
            total_contribution = round(epf_contri_remitted + eps_contri_remitted + epf_eps_diff_remitted + admin + edli_admin)



            employee["epf_wages"] = epf_wages
            employee["eps_wages"] = eps_wages
            employee["edli_wages"] = edli_wages
            employee["epf_contri_remitted"] = epf_contri_remitted
            employee["eps_contri_remitted"] = eps_contri_remitted
            employee["epf_eps_diff_remitted"] = epf_eps_diff_remitted
            employee["admin"] = admin
            employee["edli_admin"] = edli_admin
            employee["total_contribution"] = total_contribution

            data.append(employee)

    return data

@frappe.whitelist()
def get_years():
    year_list = frappe.db.sql_list(
        """SELECT DISTINCT YEAR(end_date) FROM `tabSalary Slip` ORDER BY YEAR(end_date) DESC"""
    )
    if not year_list:
        year_list = [getdate().year]

    return "\n".join(str(year) for year in year_list)


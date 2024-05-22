# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")


def execute(filters=None):
    if not filters:
        filters = {}

    currency = None
    if filters.get("currency"):
        currency = filters.get("currency")
    company_currency = erpnext.get_company_currency(filters.get("company"))

    salary_slips = get_salary_slips(filters, company_currency)
    if not salary_slips:
        return [], []

    earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
    columns = get_columns(ded_types)

    ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
    ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

    esic_no_map = get_employee_esic_no_map()

    data = []
    for ss in salary_slips:
        row = {
            "salary_slip_id": ss.name,
            "employee": ss.employee,
            "employee_name": ss.employee_name,
            "custom_esic_no": esic_no_map.get(ss.employee),
            "payment_days": ss.payment_days,
            "total_loan_repayment": ss.total_loan_repayment,
        }

        update_column_width(ss, columns)

        for e in earning_types:
            row.update({frappe.scrub(e): ss_earning_map.get(ss.name, {}).get(e)})

        for d in ded_types:
            row.update({frappe.scrub(d): ss_ded_map.get(ss.name, {}).get(d)})

        if currency == company_currency:
            row.update(
                {
                    "gross_pay": flt(ss.gross_pay) * flt(ss.exchange_rate),
                    "total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
                    "net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
                }
            )
        else:
            row.update(
                {"gross_pay": ss.gross_pay, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
            )

        data.append(row)

    return columns, data


def get_earning_and_deduction_types(salary_slips):
    salary_component_and_type = {_("Earning"): [], _("Deduction"): []}

    for salary_compoent in get_salary_components(salary_slips):
        component_type = get_salary_component_type(salary_compoent)
        salary_component_and_type[_(component_type)].append(salary_compoent)

    return sorted(salary_component_and_type[_("Earning")]), sorted(
        salary_component_and_type[_("Deduction")]
    )


def update_column_width(ss, columns):
    if ss.branch is not None:
        columns[3].update({"width": 120})
    if ss.department is not None:
        columns[4].update({"width": 120})
    if ss.designation is not None:
        columns[5].update({"width": 120})


def get_columns(ded_types):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("ESI"),
            "fieldname": "custom_esic_no",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Payable During The Month"),
            "fieldname": "payment_days",
            "fieldtype": "Float",
            "width": 250,
        },
        {
            "label": _("Total Monthly Wages"),
            "fieldname": "gross_pay",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 200,
        },
    ]

    for deduction in ded_types:
        if deduction in ["ESI", "ESIE"]:
            label = _("ESI by Employee") if deduction == "ESI" else _("ESI by Employer")
            columns.append(
                {
                    "label": label,
                    "fieldname": frappe.scrub(deduction),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )

    columns.extend(
        [
            {
                "label": _("Reason Code for Zero workings days"), 
                "fieldname": "", 
                "fieldtype": "", 
                "width": 140
            },
            {
                "label": _("Last Working Day"),
                "fieldname": "relieving_date",
                "fieldtype": "Date",
                "width": 160,
            },
        ]
    )
    return columns


def get_salary_components(salary_slips):
    return (
        frappe.qb.from_(salary_detail)
        .where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips])))
        .select(salary_detail.salary_component)
        .distinct()
    ).run(pluck=True)


def get_salary_component_type(salary_component):
    return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)


def get_salary_slips(filters, company_currency):
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    query = frappe.qb.from_(salary_slip).select(salary_slip.star)

    if filters.get("docstatus"):
        query = query.where(salary_slip.docstatus == doc_status[filters.get("docstatus")])

    if filters.get("from_date"):
        query = query.where(salary_slip.start_date >= filters.get("from_date"))

    if filters.get("to_date"):
        query = query.where(salary_slip.end_date <= filters.get("to_date"))

    if filters.get("company"):
        query = query.where(salary_slip.company == filters.get("company"))

    if filters.get("employee"):
        query = query.where(salary_slip.employee == filters.get("employee"))

    if filters.get("currency") and filters.get("currency") != company_currency:
        query = query.where(salary_slip.currency == filters.get("currency"))

    salary_slips = query.run(as_dict=1)

    return salary_slips or []


def get_employee_esic_no_map():
    employee = frappe.qb.DocType("Employee")

    result = (frappe.qb.from_(employee).select(employee.name, employee.custom_esic_no)).run()

    return frappe._dict(result)


def get_salary_slip_details(salary_slips, currency, company_currency, component_type):
    salary_slips = [ss.name for ss in salary_slips]

    result = (
        frappe.qb.from_(salary_slip)
        .join(salary_detail)
        .on(salary_slip.name == salary_detail.parent)
        .where((salary_detail.parent.isin(salary_slips)) & (salary_detail.parentfield == component_type))
        .select(
            salary_detail.parent,
            salary_detail.salary_component,
            salary_detail.amount,
            salary_slip.exchange_rate,
        )
    ).run(as_dict=1)

    ss_map = {}

    for d in result:
        ss_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, 0.0)
        if currency == company_currency:
            ss_map[d.parent][d.salary_component] += flt(d.amount) * flt(
                d.exchange_rate if d.exchange_rate else 1
            )
        else:
            ss_map[d.parent][d.salary_component] += flt(d.amount)

    return ss_map


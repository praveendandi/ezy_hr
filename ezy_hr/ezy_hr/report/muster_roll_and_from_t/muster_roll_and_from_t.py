# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt, formatdate
import erpnext
from frappe import _

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
salary_component = frappe.qb.DocType("Salary Component")

def get_salary_structure_earnings(salary_slip_name):
    salary_structure = frappe.db.get_value("Salary Slip", salary_slip_name, "salary_structure")
    sql_query = """
        SELECT sd.salary_component, sd.amount 
        FROM `tabSalary Detail` sd 
        WHERE sd.parent = %s AND sd.amount > 0 AND sd.salary_component NOT LIKE 'Deduction%%'
    """
    earnings_data = frappe.db.sql(sql_query, (salary_structure,), as_dict=True)
    earnings_list = []
    for item in earnings_data:
        earnings_list.append({
            "salary_component": item.get("salary_component"),
            "amount": item.get("amount")
        })
    return earnings_list

def execute(filters=None):
    if not filters:
        filters = {}

    currency = filters.get("currency") or None
    company_currency = erpnext.get_company_currency(filters.get("company"))

    salary_slips = get_salary_slips(filters, company_currency)
    if not salary_slips:
        return [], []

    earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
    columns = get_columns(earning_types, ded_types)

    ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
    ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

    doj_map = get_employee_doj_map()
    dob_map = get_employee_dob()

    data = []
    for ss in salary_slips:
        employee_data = frappe.db.get_list("Employee", {"name": ss.employee}, ["name", "bank_name", "custom_gross_amount", "gender", "date_of_birth", 
        "custom_father_name", "custom_esic_no", "provident_fund_account", "total_working_days", "salary_mode"])

        for emp in employee_data:
            department_name = None
            if ss.department:
                department_name = ss.department.split(" - ")[0] if " - " in ss.department else ss.department

            actual_gross = emp.custom_gross_amount
            row = {
                "salary_slip_id": ss.name,
                "employee": ss.employee,
                "employee_name": ss.employee_name,
                "date_of_joining": formatdate(doj_map.get(ss.employee), "dd-mm-yyyy"),
                "date_of_birth": formatdate(dob_map.get(ss.employee), "dd-mm-yyyy"),
                "gender": emp.gender,
                "custom_father_name": emp.custom_father_name,
                "custom_esic_no": emp.custom_esic_no,
                "provident_fund_account": emp.provident_fund_account,
                "salary_mode": emp.salary_mode,
                "total_working_days": ss.total_working_days,
                "branch": ss.branch,
                "department": department_name,
                "designation": ss.designation,
                "attendance_device_id": emp.get("attendance_device_id", ""),
                "company": ss.company,
                "payment_days": ss.payment_days,
                "currency": currency or company_currency,
                "total_loan_repayment": ss.total_loan_repayment,
                "actual_gross_pay": actual_gross
            }

            update_column_width(ss, columns)

            salary_structure_earnings = get_salary_structure_earnings(ss.name)

            actual_basic_da = 0
            for e in earning_types:
                actual_earning_value = next(
                    (item["amount"] for item in salary_structure_earnings if item.get("salary_component") == e),
                    0
                )
                
                if e in ["Basic", "Dearness Allowance"]:
                    actual_basic_da += actual_earning_value

                row.update({
                    f"actual_{frappe.scrub(e)}": round(actual_earning_value),
                    frappe.scrub(e): round(ss_earning_map.get(ss.name, {}).get(e) or 0)
                })

            row["actual_basic_da"] = actual_basic_da

            basic_da = 0
            for e in earning_types:
                actual_earning_value = next(
                    (item["amount"] for item in salary_structure_earnings if item.get("salary_component") == e),
                    0
                )
                
                if e in ["Basic", "Dearness Allowance"]:
                    proportionate_value = actual_earning_value * (ss.payment_days / ss.total_working_days)
                    basic_da += proportionate_value

                    if e == "Basic":
                        row["basic"] = proportionate_value

                row.update({
                    f"actual_{frappe.scrub(e)}": round(actual_earning_value),
                    frappe.scrub(e): round(ss_earning_map.get(ss.name, {}).get(e) or 0)
                })

            row["basic_da"] = basic_da

            for d in ded_types:
                row.update({frappe.scrub(d): round(ss_ded_map.get(ss.name, {}).get(d) or 0)})

            net_pay = flt(ss.net_pay)
            esic_deduction = ss_ded_map.get(ss.name, {}).get("ESI", 0)
            
            # Add ESIC deduction to net pay
            net_salary_adding_esic = round(net_pay + esic_deduction)
            
            row.update({"net_salary_adding_esic": net_salary_adding_esic})

            if currency == company_currency:
                row.update(
                    {
                        "gross_pay": round(flt(ss.gross_pay) * flt(ss.exchange_rate)),
                        "total_deduction": round(flt(ss.total_deduction) * flt(ss.exchange_rate)),
                        "net_pay": round(flt(ss.net_pay) * flt(ss.exchange_rate)),
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

    for salary_component in get_salary_components(salary_slips):
        component_type = get_salary_component_type(salary_component)
        salary_component_and_type[_(component_type)].append(salary_component)

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
    if ss.leave_without_pay is not None:
        columns[9].update({"width": 120})

def get_columns(earning_types, ded_types):
    not_include_net = []

    # Reorder earning types to place "City Compensatory Allowance" and "House Rent Allowance" as desired
    reordered_earning_types = ["House Rent Allowance", "City Compensatory Allowance"]
    remaining_earning_types = [e for e in earning_types if e not in reordered_earning_types]
    earning_types = reordered_earning_types + remaining_earning_types

    columns = [
        {
            "label": _("Unit Name"),
            "fieldname": "company",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "label": _("Emp No"),
            "fieldname": "employee",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Name of the Employees"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 140,
        },
        {
            "label": _("Department"),
            "fieldname": "department",
            "fieldtype": "Data",
            "width": -1,
        },
        {
            "label": _("Designation"),
            "fieldname": "designation",
            "fieldtype": "Link",
            "options": "Designation",
            "width": 120,
        },
        {
            "label": _("Father / Husband Name"),
            "fieldname": "custom_father_name",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Sex"),
            "fieldname": "gender",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Date of Birth"),
            "fieldname": "date_of_birth",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Date of Joining"),
            "fieldname": "date_of_joining",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("ESI Numbers"),
            "fieldname": "custom_esic_no",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("UAN Numbers"),
            "fieldname": "provident_fund_account",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": _("Working  Days"),
            "fieldname": "total_working_days",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Actual Basic+ DA"),
            "fieldname": "actual_basic_da",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        }
    ]

    for e in earning_types:
        if e not in ["Basic", "Dearness Allowance"]:
            columns.append(
                {
                    "label": f"Actual {e}",
                    "fieldname": f"actual_{frappe.scrub(e)}",
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )
    columns.append(
        {
            "label": _("Total Gross"),
            "fieldname": "actual_gross_pay",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        }
    )

    columns += [
        {
            "label": _("Payment Days"),
            "fieldname": "payment_days",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Basic+ DA"),
            "fieldname": "basic_da",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 140,
        }
    ]
    
    for e in earning_types:
        if e not in ["Basic", "Dearness Allowance"]:
            columns.append(
                {
                    "label": e,
                    "fieldname": frappe.scrub(e),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )

    columns.append(
        {
            "label": _("Earned Gross Total"),
            "fieldname": "gross_pay",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 150,
        }
    )

    for deduction in ded_types:
        if deduction not in ["PF-Employer", "ESIE","Actual PF Employer"]:
            columns.append(
                {
                    "label": deduction,
                    "fieldname": frappe.scrub(deduction),
                    "fieldtype": "Currency",
                    "options": "currency",
                    "width": 120,
                }
            )
        else:
            not_include_net.append(frappe.scrub(deduction))

    columns += [
        {
            "label": _("Total Deduction"),
            "fieldname": "total_deduction",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Net Pay"),
            "fieldname": "net_pay",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120,
        },
        {
            "label": _("Net Salary Adding ESIC"),
            "fieldname": "net_salary_adding_esic",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": _("Mode of Payment"),
            "fieldname": "salary_mode",
            "fieldtype": "Data",
            "width": 120,
        },
    ]

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

def get_employee_doj_map():
    return frappe._dict(
        frappe.get_all("Employee", fields=["name", "date_of_joining"], as_list=1)
    )

def get_employee_dob():
    return frappe._dict(
        frappe.get_all("Employee", fields=["name", "date_of_birth"], as_list=1)
    )

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

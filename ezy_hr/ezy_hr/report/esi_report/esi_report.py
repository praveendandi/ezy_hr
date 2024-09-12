# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import flt
from datetime import datetime,date
from erpnext.accounts.utils import get_fiscal_year
import erpnext

salary_slip = frappe.qb.DocType("Salary Slip")
salary_detail = frappe.qb.DocType("Salary Detail")
employee = frappe.qb.DocType("Employee")

def execute(filters=None):
    if filters is None:
        filters = {}

    currency = filters.get("currency")
    company_currency = erpnext.get_company_currency(filters.get("company"))

    salary_slips = get_salary_slips(filters, company_currency)
    if not salary_slips:
        return [], []

    stipend_employees = get_stipend_employees()

    salary_slips = [ss for ss in salary_slips if ss.employee not in stipend_employees]

    earning_types, ded_types = get_earning_and_deduction_types(salary_slips)
    ss_earning_map = get_salary_slip_details(salary_slips, currency, company_currency, "earnings")
    ss_ded_map = get_salary_slip_details(salary_slips, currency, company_currency, "deductions")

    columns = get_columns(ded_types)
    esic_no_map, relieving_date_map, gross_amount_map = get_employee_details()

    data = []
    for ss in salary_slips:
        gross_amount = gross_amount_map.get(ss.employee, 0)
        
        esi_condit = esi_conditions(ss)
        _, start_date, end_date = get_fiscal_year(ss.start_date)
        is_applicable = process_esi(ss, esi_condit, start_date, end_date)
        
        if is_applicable:

            row = {
                "salary_slip_id": ss.name,
                "employee": ss.employee,
                "employee_name": ss.employee_name,
                "custom_esic_no": esic_no_map.get(ss.employee),
                "payment_days": ss.payment_days,
                "total_loan_repayment": ss.total_loan_repayment,
                "relieving_date": relieving_date_map.get(ss.employee),
                "custom_reason_for_esi": ss.custom_reason_for_esi
            }
            incentive_amount = 0
            nfh_amount = 0
            earn_gross = 0

            for e in earning_types:
                if e == "Incentive":
                    if ss_earning_map.get(ss.name,{}).get(e):
                        incentive_amount = ss_earning_map.get(ss.name).get(e, 0)
                if e == "NFH Wages":
                    if ss_earning_map.get(ss.name,{}).get(e):
                        nfh_amount = ss_earning_map.get(ss.name).get(e, 0)

            for d in ded_types:
                if ss_ded_map.get(ss.name, {}).get(d):
                    row[frappe.scrub(d)] = ss_ded_map.get(ss.name).get(d, 0)

            if flt(ss.gross_pay-(incentive_amount+nfh_amount))>=21000:
                earn_gross = flt((21000/ss.total_working_days)*ss.payment_days)
            else:
                earn_gross = flt(ss.gross_pay-(incentive_amount+nfh_amount))
                
            if currency == company_currency:
                row.update(
                    {
                        "gross_pay": earn_gross * flt(ss.exchange_rate),
                        "total_deduction": flt(ss.total_deduction) * flt(ss.exchange_rate),
                        "net_pay": flt(ss.net_pay) * flt(ss.exchange_rate),
                    }
                )
            else:
                row.update(
                    {"gross_pay": earn_gross, "total_deduction": ss.total_deduction, "net_pay": ss.net_pay}
                )

            data.append(row)

    return columns, data

def process_esi(doc, cycle, start_date, end_date):
    
    current_year = start_date.year
    end_year = end_date.year if not cycle["is_first_cycle"] else current_year
    date_range = cycle["range_date"].split("-")
    name = f"{doc.employee}-({date_range[0]} {current_year})-({date_range[1]} {end_year})"

    esi_exists = frappe.get_list("ESI Applicable List", filters={'id': name, "employee": doc.employee}, fields=["name"])
    if esi_exists:
       return True
    else:
        return False
   
def esi_conditions(ss):
    
    if isinstance(ss.start_date,str):
        current_date = datetime.strptime(ss.start_date, "%Y-%m-%d").date()
    else:
        current_date = ss.start_date
        
    settings = frappe.get_doc("EzyHr Settings")
    
    if current_date.month in range(4, 10):
        return {
            "range_date": f"{settings.f_start_month}-{settings.f_end_month}",
            "is_first_cycle": True,
        }
    else:
        return {
            "range_date": f"{settings.s_start_month}-{settings.s_end_month}",
            "is_first_cycle": False,
        }

def get_earning_and_deduction_types(salary_slips):
    earning_types, ded_types = [], []

    for salary_component in get_salary_components(salary_slips):
        component_type = get_salary_component_type(salary_component)
        if component_type == "Earning":
            earning_types.append(salary_component)
        elif component_type == "Deduction":
            ded_types.append(salary_component)

    return sorted(earning_types), sorted(ded_types)

def get_columns(ded_types):
    columns = [
        {
            "label": _("Employee"), 
            "fieldname": "employee", 
            "fieldtype": "Data", 
            "width": 120
        },
        {
            "label": _("ESI No"), 
            "fieldname": "custom_esic_no", 
            "fieldtype": "Data", 
            "width": 160
        },
        {
            "label": _("Employee Name"), 
            "fieldname": "employee_name", 
            "fieldtype": "Data", 
            "width": 140
        },
        {
            "label": _("No of Days For Which Wages Paid"), 
            "fieldname": "payment_days", 
            "fieldtype": "Float", 
            "width": 160
        },
        {
            "label": _("Total Monthly Wages"), 
            "fieldname": "gross_pay", 
            "fieldtype": "Currency", 
            "options": "currency", 
            "width": 160
        },
    ]

    for deduction in ded_types:
        if deduction in ["ESI", "ESIE"]:
            label = _("ESI By Employee") if deduction == "ESI" else _("ESI By Employer")
            columns.append(
                {
                    "label": label, 
                    "fieldname": frappe.scrub(deduction), 
                    "fieldtype": "Currency", 
                    "options": "Currency", 
                    "width": 160
                }
            )

    columns.extend(
        [
            {
                "fieldname": "custom_reason_for_esi",
                "label": _("Reason Code For Zero Workings Days"),
                "fieldtype": "Data",
            },
            {
                "label": _("Last Working Day"), 
                "fieldname": "relieving_date", 
                "fieldtype": "Date", 
                "width": 160
            },
        ]
    )
    return columns

def get_salary_components(salary_slips):
    return frappe.qb.from_(salary_detail) \
        .where((salary_detail.amount != 0) & (salary_detail.parent.isin([d.name for d in salary_slips]))) \
        .select(salary_detail.salary_component) \
        .distinct().run(pluck=True)

def get_salary_component_type(salary_component):
    return frappe.db.get_value("Salary Component", salary_component, "type", cache=True)

def get_salary_slips(filters, company_currency):
    doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

    query = frappe.qb.from_(salary_slip).select(
        salary_slip.star
    )

    if filters.get("docstatus"):
        query = query.where(salary_slip.docstatus == doc_status.get(filters.get("docstatus")))

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

    salary_slips = query.run(as_dict=True)

    return salary_slips or []

def get_employee_details():
    result = frappe.qb.from_(employee).select(employee.name, employee.custom_esic_no, employee.relieving_date, employee.custom_gross_amount).run(as_dict=True)
    esic_no_map = {r.name: r.custom_esic_no for r in result}
    relieving_date_map = {r.name: r.relieving_date for r in result}
    gross_amount_map = {r.name: r.custom_gross_amount for r in result}
    return esic_no_map, relieving_date_map, gross_amount_map

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
    ).run(as_dict=True)

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

def get_stipend_employees():
    stipend_employees = frappe.qb.from_(salary_detail) \
        .join(salary_slip).on(salary_slip.name == salary_detail.parent) \
        .where(salary_detail.salary_component == "Stipend") \
        .select(salary_slip.employee) \
        .distinct().run(pluck=True)
    return stipend_employees




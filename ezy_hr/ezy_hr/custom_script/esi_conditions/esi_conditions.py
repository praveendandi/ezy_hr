import frappe
from datetime import datetime , timedelta
from frappe import _
import sys
import traceback
from erpnext.accounts.utils import get_fiscal_year


def get_salary_cycle(date):
    settings = frappe.get_doc("EzyHr Settings")
    if date.month in range(4, 10):
        return {"range_date": f"{settings.f_start_month}-{settings.f_end_month}", "is_first_cycle": True}
    else:
        return {"range_date": f"{settings.s_start_month}-{settings.s_end_month}", "is_first_cycle": False}

def get_custom_fiscal_year(payroll_date):
    _, start_date, end_date = get_fiscal_year(payroll_date)
    return start_date, end_date

def create_esi_application(row_date, name, employee, company, start_date, end_date, start_year, end_year):
    if row_date.get("base") <= 21000:
        esi_doc = frappe.get_doc({
            "doctype": "ESI Applicable List",
            "id": name,
            "employee": employee,
            "unit": company,
            "start_date": start_date,
            "end_date": end_date,
            "start_year": start_year,
            "end_year": end_year,
            "actual_base": row_date.get("base"),
            "esi": row_date.get("base") * 0.0075,
            "esie": row_date.get("base") * 0.0325,
            "s_assignment_id": row_date.get("name")
        })
        esi_doc.insert()
        frappe.db.commit()
        return True
    return False

def update_esi(name, employee):
    latest_doc = frappe.db.get_list("Salary Structure Assignment",{"employee":employee,"docstatus":1},["name","base"],order_by="from_date desc",limit=1)
    esi_data = frappe.get_list("ESI Applicable List", filters={'id': name, "employee": employee}, fields=["esi", "esie"])
    
    if esi_data:
        esi_values = {"custom_esi": esi_data[0].get("esi"), "custom_esie": esi_data[0].get("esie")}
    else:
        esi_values = {"custom_esi": 0, "custom_esie": 0}
        
    frappe.db.set_value("Salary Structure Assignment", {"name": latest_doc[0].get("name"), "employee": employee}, esi_values)
    frappe.db.commit()

def process_esic_for_employee(doc, employee):
    if isinstance(doc.start_date,str):
        convert_date = datetime.strptime(doc.start_date, "%Y-%m-%d").date()
    else:
        convert_date = doc.start_date
        
    salary_cycle = get_salary_cycle(convert_date)
    start_date, end_date = get_custom_fiscal_year(convert_date)
    employee_doc,company = frappe.get_value("Employee", {"name": employee.employee, "employee": employee.employee}, ["employee_name", "company"])

    if company:
        existing_entries = frappe.get_all("Salary Structure Assignment", filters={"employee": employee.employee, "docstatus": 1}, fields=["from_date", "name", "salary_structure", "base"], order_by="from_date desc", limit=2)

        if not existing_entries:
            frappe.log_error(f"No Salary Structure Assignments found for employee {employee.employee}")
            return

        current_year = start_date.year
        range_month = salary_cycle["range_date"].split("-")
        name = f"{employee.employee}-({range_month[0]} {current_year})-({range_month[1]} {end_date.year if not salary_cycle['is_first_cycle'] else current_year})"
                
        esi_detail = frappe.get_list("ESI Applicable List", filters={'id': name, "employee": employee.employee}, fields=["name"])

        if not esi_detail:
            row_date = existing_entries[0]
            is_created = create_esi_application(row_date, name, employee.employee, company, start_date=range_month[0], end_date=range_month[1], start_year=current_year, end_year=end_date.year if not salary_cycle['is_first_cycle'] else current_year)
            update_esi(name, employee.employee)
        else:
            update_esi(name, employee.employee)

@frappe.whitelist()
def esi_conditions(doc, method=None):
    try:
        for employee in doc.employees:
            process_esic_for_employee(doc, employee)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(f"line No:{exc_tb.tb_lineno}\n{traceback.format_exc()}", "esi_conditions")

import frappe
from datetime import datetime , timedelta
from frappe import _
import sys
import traceback
from erpnext.accounts.utils import get_fiscal_year


def get_salary_cycle(date):
    
    settings = frappe.get_doc("EzyHr Settings")
    if date.month in range(4, 10):
        return {
            "range_date": f"{settings.f_start_month}-{settings.f_end_month}",
            "is_first_cycle": True,
        }
    else:
        return {
            "range_date": f"{settings.s_start_month}-{settings.s_end_month}",
            "is_first_cycle": False,
        }

def get_custom_fiscal_year(from_date):
    _, start_date, end_date = get_fiscal_year(from_date)
    return start_date, end_date

def create_esi_application(doc, name, start_date, end_date, start_year, end_year):
    if doc.base <= 21000:
        esi_doc = frappe.get_doc({
            "doctype": "ESI Applicable List",
            "id": name,
            "employee": doc.employee,
            "unit": doc.company,
            "start_date": start_date,
            "end_date": end_date,
            "start_year": start_year,
            "end_year": end_year,
            "actual_base": doc.get("base"),
            "esi": doc.get("base") * 0.0075,
            "esie": doc.get("base") * 0.0325,
            "s_assignment_id": doc.name
        })
        esi_doc.insert()
        frappe.db.commit()

def update_esi(doc, name):
    esi_data = frappe.get_list("ESI Applicable List", filters={'id': name, "employee": doc.employee}, fields=["esi", "esie"])
    if esi_data:
        esi_values = {"custom_esi": esi_data[0].get("esi"), "custom_esie": esi_data[0].get("esie")}
    else:
        esi_values = {"custom_esi": 0, "custom_esie": 0}
        
    frappe.db.set_value("Salary Structure Assignment", {"name": doc.get("name"), "employee": doc.employee}, esi_values)
    frappe.db.commit()

def process_esi(doc, cycle, start_date, end_date):
    current_year = start_date.year
    end_year = end_date.year if not cycle["is_first_cycle"] else current_year
    date_range = cycle["range_date"].split("-")
    name = f"{doc.employee}-({date_range[0]} {current_year})-({date_range[1]} {end_year})"

    esi_exists = frappe.get_list("ESI Applicable List", filters={'id': name, "employee": doc.employee}, fields=["name"])
    if not esi_exists:
        create_esi_application(doc, name, date_range[0], date_range[1], current_year, end_year)
    update_esi(doc, name)

def set_esi_for_employee(doc, method=None):
    try:
        employee_docs = frappe.get_list("Employee",filters={ "name": ["not like", "%-T%"],"employee": doc.employee},fields=["name", "employee_name", "employee","company"])
        if employee_docs:
            if isinstance(doc.from_date,str):
                current_date = datetime.strptime(doc.from_date, "%Y-%m-%d").date()
            else:
                current_date = doc.from_date
                
            cycle = get_salary_cycle(current_date)
            start_date, end_date = get_custom_fiscal_year(current_date)
            process_esi(doc, cycle, start_date, end_date)
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error(f"Line No:{exc_tb.tb_lineno}\n{traceback.format_exc()}", "set_esi_for_employee")

def on_cancel_of_ssa(doc, method=None):
    try:
        if isinstance(doc.from_date,str):
            current_date = datetime.strptime(doc.from_date, "%Y-%m-%d").date()
        else:
            current_date = doc.from_date
            
        cycle = get_salary_cycle(current_date)
        start_date, end_date = get_custom_fiscal_year(current_date)
        current_year = start_date.year
        end_year = end_date.year if not cycle["is_first_cycle"] else current_year
        date_range = cycle["range_date"].split("-")
        name = f"{doc.employee}-({date_range[0]} {current_year})-({date_range[1]} {end_year})"

        frappe.db.delete("ESI Applicable List", {"employee": doc.employee, "id": name})
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"delete_salary_revision: {e}")

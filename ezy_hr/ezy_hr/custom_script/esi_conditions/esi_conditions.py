import frappe
from datetime import datetime
from frappe import _
import sys
import traceback

def get_salary_cycle(date):
    
    settings = frappe.get_doc("EzyHr Settings")
    
    if date.month in range(4, 10):
        first_contribution_cycle = {
            "range_date":f"{settings.f_start_month}-{settings.f_end_month}",
            "first_contribution_cycle":True,
            "second_contribution_cycle":False
        }
        return first_contribution_cycle
    else:
        second_contribution_cycle = {
            "range_date":f"{settings.s_start_month}-{settings.s_end_month}",
            "second_contribution_cycle":True,
            "first_contribution_cycle":False,
        }
        return second_contribution_cycle
    

def process_esic_for_employee(doc, each_empl):
    
    convert_date = datetime.strptime(doc.start_date, "%Y-%m-%d").date()
    salary_cycle = get_salary_cycle(convert_date)

    # current_cycle_start, current_cycle_end = get_cycle_dates(salary_cycle, convert_date.year)
   
    # start_date = current_cycle_start.date()
    # end_date = current_cycle_end.date()
    
    employee_docs = frappe.get_list("Employee",filters={ "name": ["not like", "%-T%"],"employee": each_empl.employee},fields=["name", "employee_name", "employee"])
    
    if employee_docs:
        existing_entries = frappe.db.sql('''
            SELECT from_date, name, salary_structure, base 
            FROM `tabSalary Structure Assignment`
            WHERE employee = %s AND docstatus = 1
            ORDER BY creation ASC
        ''', (employee_docs[0]['employee']), as_dict=1)


        if not existing_entries:
            frappe.log_error("No Salary Structure Assignments found for employee {}".format(each_empl.employee))
            return

        if salary_cycle.get("first_contribution_cycle"):
            row_date = existing_entries[0]
            calculate_esi(doc, row_date, convert_date, each_empl)

        if salary_cycle.get("second_contribution_cycle"):
            row_date = existing_entries[1] if len(existing_entries) > 1 else existing_entries[0]
            frappe.log_error("row_data",row_date)
            calculate_esi(doc, row_date, convert_date, each_empl)


def calculate_esi(doc, row_date, convert_date, each_empl):
    
    latest_doc = frappe.db.get_list("Salary Structure Assignment",filters={"employee":each_empl.employee,"docstatus":1}, fields=["name"],order_by="creation desc",limit=2)
    if row_date.get("base") <= 21000:
        
        custom_esi = row_date.get("base")  * 0.0075
        custom_esie = row_date.get("base") * 0.0325
        
        frappe.db.set_value(
            "Salary Structure Assignment",
            {"name": latest_doc[0].get("name"), "employee": each_empl.employee},
            {"custom_esi": custom_esi, "custom_esie": custom_esie}
        )
        frappe.db.commit()
    else:
        if row_date.get("base") <= 21000:
            custom_esi = row_date.get("base")  * 0.0075
            custom_esie = row_date.get("base") * 0.0325
            
            frappe.db.set_value(
                "Salary Structure Assignment",
                {"name": latest_doc[0].get("name"), "employee": each_empl.employee},
                {"custom_esi": custom_esi, "custom_esie": custom_esie}
            )
            frappe.db.commit()
        else:
            frappe.db.set_value(
                "Salary Structure Assignment",
                {"name": latest_doc[0].get("name"), "employee": each_empl.employee},
                {"custom_esi": 0, "custom_esie": 0}
                )
            frappe.db.commit()
        
            frappe.log_error("Base salary exceeds limit for ESI calculation for employee {}".format(each_empl.employee))


# def get_cycle_dates(salary_cycle, year):
        
#     if salary_cycle.get('range_date') == 'Apr-Sept':
#         return (datetime(year, 4, 1), datetime(year, 9, 30))
#     else:
#         return (datetime(year, 10, 1), datetime(year+1, 3, 31))


@frappe.whitelist()
def esi_conditions(doc,method=None):
    try:
        for each_empl in doc.employees:
            process_esic_for_employee(doc,each_empl)
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "esi_conditions")

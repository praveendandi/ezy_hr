import frappe
from datetime import datetime
from frappe import _
import calendar
from hrms.hr.report.monthly_attendance_sheet.monthly_attendance_sheet import execute as execute_


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

    current_cycle_start, current_cycle_end = get_cycle_dates(salary_cycle, convert_date.year)
    start_date = current_cycle_start.date()
    end_date = current_cycle_end.date()

    existing_entries = frappe.db.sql('''
        SELECT from_date, name, salary_structure, base 
        FROM `tabSalary Structure Assignment`
        WHERE employee = %s AND docstatus = 1 
        AND creation BETWEEN %s AND %s
        ORDER BY creation ASC
    ''', (each_empl.employee, start_date, end_date), as_dict=1)


    if not existing_entries:
        frappe.log_error("No Salary Structure Assignments found for employee {}".format(each_empl.employee))
        return

    if start_date <= convert_date <= end_date and salary_cycle.get("first_contribution_cycle"):
        row_date = existing_entries[0]
        calculate_esi(doc, row_date, convert_date, each_empl)

    if start_date <= convert_date <= end_date and salary_cycle.get("second_contribution_cycle"):
        row_date = existing_entries[-1] if len(existing_entries) > 1 else existing_entries[0]
        calculate_esi(doc, row_date, convert_date, each_empl)


def calculate_esi(doc, row_date, convert_date, each_empl):
    days_in_month = get_number_of_days(convert_date)
    total_pays = get_no_of_payment_days(each_empl.employee, convert_date, doc.company)

    if row_date.get("base") <= 21000:
        custom_esi = ((row_date.get("base") / days_in_month) * total_pays) * 0.0075
        custom_esie = ((row_date.get("base") / days_in_month) * total_pays) * 0.0325
        
        lates_doc = frappe.db.get_list("Salary Structure Assignment",filters={"employee":each_empl.employee,"docstatus":1}, fields=["name"], order_by= "creation desc", limit=1)
        
        frappe.db.set_value(
            "Salary Structure Assignment",
            {"name": lates_doc[0].get("name"), "employee": each_empl.employee},
            {"custom_esi": custom_esi, "custom_esie": custom_esie}
        )
        frappe.db.commit()
    else:
        frappe.log_error("Base salary exceeds limit for ESI calculation for employee {}".format(each_empl.employee))


def get_cycle_dates(salary_cycle, year):
   
    if salary_cycle.get('range_date') == 'Apr-Sept':
        return (datetime(year, 4, 1), datetime(year, 9, 30))
    else:
        return (datetime(year, 10, 1), datetime(year + 1, 3, 31))

def get_no_of_payment_days(employee_id,date,company):
    
    filters={
        "month":date.month,
        "year":date.year,
        "employee":employee_id
        ,"company":company,
        "summarized_view":1
    }
    
    total_days = 0
    
    row_attendance = execute_(filters)
    if len(row_attendance[1])>0:
        get_total_working_day = row_attendance[1]
        for each_ in get_total_working_day:
            total_present = each_['total_present']
            total_leaves = each_['total_leaves']
            total_holidays = each_['total_holidays']
            leave_without_pay = each_['leave_without_pay']
            unmarked_days = each_['unmarked_days']
            total_days = (total_present + total_leaves + total_holidays+unmarked_days) - leave_without_pay
            
        return total_days

@frappe.whitelist()
def esi_conditions(doc,method=None):
    try:
        for each_empl in doc.employees:
            process_esic_for_employee(doc,each_empl)
            
    except Exception as e:
        frappe.log_error("esi_conditions",str(e))
        

def get_number_of_days(start_date):
    
    year = start_date.year
    month = start_date.month
    
    days_in_month = calendar.monthrange(year, month)[1]
    return days_in_month

import frappe
import erpnext
from frappe.model.meta import Meta
from datetime import datetime

def creating_additional_earn_and_com_off(doc,method=None):
    try:
        holiday_name = frappe.db.get_value("Employee",{"name":doc.employee},['holiday_list'])
        
        data = {
            "from_date": doc.start_date,
            "to_date": doc.end_date,
            "name":holiday_name
        }
        
        employee_list = get_employees(data,doc)
        
        if employee_list:
            resutl = creating_addition(employee_list,doc)
            
            if resutl:
                doc.save()
                frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error addition salary structure: {e}")   
    
def get_employees(data, doc):
    # Define the holiday filters
    holiday_filters = [
        ["holiday_date", ">=", data["from_date"]],
        ["holiday_date", "<=", data["to_date"]],
        ["parent", "=", data["name"]],
        ["weekly_off","=",0]
    ]

    # Fetch holidays based on the filters
    holidays = frappe.get_all(
        "Holiday",
        fields=["holiday_date", "description"],
        filters=holiday_filters
    )
    
    unit = doc.company
    employee_id = doc.employee
    holiday_names = {holiday["holiday_date"]: holiday["description"] for holiday in holidays}
    holidays_list = [holiday["holiday_date"] for holiday in holidays]

    if holidays_list:
        
        conditions = """
            attendance_date IN %(holidays_list)s 
            AND status NOT IN ('On Leave', 'Absent') 
            AND company = %(unit)s 
            AND employee = %(employee_id)s
        """

        # Fetch employee attendance data based on the conditions
        employee_list = frappe.db.sql(
            f"""
            SELECT
                employee, employee_name, attendance_date
            FROM
                `tabAttendance`
            WHERE
                {conditions}
            """,
            {"holidays_list": holidays_list, "unit": unit, "employee_id": employee_id},
            as_dict=True
        )
        
        earning_on_hod_employee = []
        employee_detail = {}

        for employee_data in employee_list:
            # Check if the employee exists and custom_apply_for_nfh_wages is 1
            if frappe.db.exists("Employee", {"name": employee_data.get("employee"), "custom_apply_for_nfh_wages": 1}) and holiday_names.get(employee_data["attendance_date"]) != "Sunday":
               
                employee_id = employee_data.get("employee")
                if employee_id:
                    if employee_id not in employee_detail:
                        employee_detail[employee_id] = {
                            "employee": employee_id,
                            "employee_name": employee_data.get("employee_name"),
                            "attendance_date": [employee_data.get("attendance_date")],
                            "holiday_description": [holiday_names.get(employee_data["attendance_date"])],
                            "no_of_day": 1,
                            "company":doc.company
                        }
                    else:
                        employee_detail[employee_id]['attendance_date'].append(employee_data.get("attendance_date"))
                        employee_detail[employee_id]['holiday_description'].append(holiday_names.get(employee_data["attendance_date"]))
                        employee_detail[employee_id]['no_of_day'] += 1

        if employee_detail:
            for each_day in employee_detail.values():
                earning_on_hod_employee.append(each_day)

        return earning_on_hod_employee
    else:
        return []


def creating_addition(empl_detail,data):
    
    for each_item in empl_detail:
        
        is_new_joining = False
        
        gross_amount,date_of_joining = frappe.db.get_value("Employee",{"name":each_item.get("employee")},['custom_gross_amount',"date_of_joining"])
        
        start_date = datetime.strptime(data.start_date,"%Y-%m-%d").date()
        
        end_date = datetime.strptime(data.end_date,"%Y-%m-%d").date()
        
        if start_date <= date_of_joining <= end_date:
            is_new_joining = True
               
        nfh_Wages_per_day = round(gross_amount/30)*each_item.get("no_of_day")
        
        details = {
            "doctype": "Additional Salary",
            "employee":each_item.get("employee"),
            "amount":nfh_Wages_per_day,
            "payroll_date":date_of_joining if is_new_joining else data.start_date ,
            "salary_component":"NFH Wages",
            "currency":"INR",
            "company":each_item.get("company")
        }
        additon_salary = frappe.get_doc(details)
        additon_salary.insert()
        additon_salary.submit()
        frappe.db.commit()
        
    return additon_salary


def cancel_addition_salary(doc,mothod=None):
    try:
        addition_cencel = frappe.db.delete("Additional Salary", {
            "employee": doc.get("employee"),
            "salary_component":"NFH Wages",
            "payroll_date": ["Between",[doc.start_date,doc.end_date]],
            "docstatus": 1,
        })
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"cancel_addition_salary: {e}") 
        
        
        
    

import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_employees_with_birthday_today():
    today = getdate()
    month = today.month
    day = today.day
    employees = frappe.db.sql("""
        SELECT name, employee_name, image
        FROM `tabEmployee` 
        WHERE 
            status = 'Active'
            AND MONTH(date_of_birth) = %s
            AND DAY(date_of_birth) = %s
    """, (month, day), as_dict=True)

    employee_data = [
        {
            'name': emp.get('employee_name'),
            'image': emp.get('image') 
        }
        for emp in employees
    ]

    return employee_data

@frappe.whitelist()
def get_employees_with_date_of_joining():
    today = getdate()
    month = today.month
    day = today.day

   
    employees = frappe.db.sql("""
        SELECT name, employee_name, image
        FROM `tabEmployee` 
        WHERE 
            status = 'Active'
            AND MONTH(date_of_joining) = %s
            AND DAY(date_of_joining) = %s
    """, (month, day), as_dict=True)

   
    employee_data = [
        {
            'name': emp.get('employee_name'),
            'image': emp.get('image') 
        }
        for emp in employees
    ]

    return employee_data
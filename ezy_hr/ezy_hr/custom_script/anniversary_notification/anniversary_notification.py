import frappe
from frappe.utils import getdate, today

@frappe.whitelist()
def anniversary_notification():
    current_date = getdate(today())
    current_month = current_date.month
    current_day = current_date.day
    
    employees = frappe.get_all("Employee", filters={"date_of_joining": ["is", "set"]}, fields=['employee_name', 'user_id', 'date_of_joining', 'company'])
    
    anniversary_employees = []
    for employee in employees:
        doj = getdate(employee['date_of_joining'])
        if doj.month == current_month and doj.day == current_day:
            anniversary_employees.append(employee)
    
    for employee in anniversary_employees:
        send_anniversary_email(employee)
    
    return anniversary_employees

def send_anniversary_email(employee):
    try:
        notification = frappe.get_doc("Notification", "Anniversary Notification")
        doj = getdate(employee['date_of_joining'])
        current_year = getdate(today()).year
        joining_year = doj.year
        years_of_service = current_year - joining_year
        
        context = {
            'employee_name': employee['employee_name'],
            'years_of_service': years_of_service,
            'company': employee['company']
        }
        
        message = frappe.render_template(notification.message, context)
        subject = f"Happy Work Anniversary, {employee['employee_name']}!"
        
        frappe.sendmail(recipients=employee['user_id'], subject=subject, message=message, now=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Failed to send anniversary email to {employee['employee_name']}")

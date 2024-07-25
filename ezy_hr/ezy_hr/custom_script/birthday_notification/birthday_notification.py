import frappe
from frappe.utils import getdate, today

@frappe.whitelist()
def birthday_notification():
    current_date = getdate(today())
    current_month = current_date.month
    current_day = current_date.day
    
    employees = frappe.get_all("Employee", filters={"date_of_birth": ["is", "set"]}, fields=['employee_name', 'user_id', 'date_of_birth', 'company'])
    
    birthday_employees = []
    for employee in employees:
        dob = getdate(employee['date_of_birth'])
        if dob.month == current_month and dob.day == current_day:
            birthday_employees.append(employee)
    
    for employee in birthday_employees:
        send_birthday_email(employee)
    # print('------------------------')
    return birthday_employees

def send_birthday_email(employee):
    notification = frappe.get_doc("Notification", "Birthday Notification Template") 
    context = {
        'doc': employee
    }
    message = frappe.render_template(notification.message, context)
    subject = f"Happy Birthday, {employee['employee_name']}!"
    
    frappe.sendmail(recipients=employee['user_id'], subject=subject, message=message,now=True)

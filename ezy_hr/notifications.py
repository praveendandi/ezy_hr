import frappe
from frappe.utils import getdate, today
from collections import defaultdict


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
   return birthday_employees

def send_birthday_email(employee):
   notification = frappe.get_doc("Notification", "Birthday Notification") 
   context = {
       'doc': employee
   }
   message = frappe.render_template(notification.message, context)
   subject = f"Happy Birthday, {employee['employee_name']}!"
   
   frappe.sendmail(recipients=employee['user_id'], subject=subject, message=message,now=True)



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



@frappe.whitelist()
def send_checkins_notification():
   employees = frappe.get_all("Employee", filters={"reports_to": ["is", "set"]}, fields=['name', 'reports_to'])
   
   grouped_employees = defaultdict(list)
   for emp in employees:
       grouped_employees[emp['reports_to']].append(emp['name'])
   
   missing_checkins = frappe.get_all("Employee Missing Checkins Request", fields=['employee', 'status', 'date', 'unit', 'employee_name', 'out_time', 'in_time'])
   
   matched_data = {
       reports_to: [
           {
               'Employee': checkin['employee'],
               'Employee Name': checkin['employee_name'],
               'Unit': checkin['unit'],
               'Date': checkin['date'],
               'First Checkin': checkin['in_time'],
               'Last CheckedOut': checkin['out_time'],
               'Status': checkin['status']
           }
           for checkin in missing_checkins if checkin['employee'] in grouped_employees[reports_to]
       ]
       for reports_to in grouped_employees
       if any(checkin['employee'] in grouped_employees[reports_to] for checkin in missing_checkins)
   }
   
   try:
       notification_doc = frappe.get_doc("Notification", {"name": "Missing Chechins Notification"})
       
       for reports_to, checkins in matched_data.items():
           context = {"checkins": checkins}
           message = frappe.render_template(notification_doc.message, context)
           subject = frappe.render_template(notification_doc.subject, context)
           
           reports_to_email = frappe.get_value("Employee", reports_to, "prefered_email")
           
           if reports_to_email:
               frappe.sendmail(
                   recipients=[reports_to_email],
                   subject=subject,
                   message=message,
                   now=True
               )
               
               frappe.publish_realtime('notification', {
                   'message': message,
                   'subject': subject
               }, user=reports_to_email)
           
   except frappe.DoesNotExistError:
       frappe.log_error("Notification named 'Checkins' not found")
   
   return matched_data



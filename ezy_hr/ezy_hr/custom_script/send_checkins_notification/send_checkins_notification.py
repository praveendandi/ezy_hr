import frappe
from collections import defaultdict
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
        notification_doc = frappe.get_doc("Notification", {"name": "Chechins"})
        
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

import frappe 
from frappe.utils import today, add_days, getdate, time_diff_in_hours
from frappe.utils.background_jobs import enqueue
from collections import defaultdict
from datetime import date
from frappe.utils.data import (
    get_first_day
)


def approval_notifications():
    # yesterday = add_days(today(), -1)
    today = date.today()
    
    # first_day_of_month = date(today.year, today.month, 1)
    first_date = get_first_day(today)
    

    employees = frappe.get_all("Employee", 
                               filters={"status": "Active", "name": ["not in", ["PRH-01", "PRH-12", "PRH-05", "PRH-03", "PRH-04"]]}, 
                               fields=["name", "employee_name", "user_id", "reports_to", "holiday_list"])
    
    attendance_issues = defaultdict(list)
    for employee in employees:
        leave_application = frappe.get_all("Leave Application", 
                                    filters={
                                        "employee": employee.name,
                                        # "posting_date": first_day_of_month,
                                        "posting_date": ["between", [first_date, today]],
                                        "docstatus": ["in", [0]],
                                        "workflow_state":"Approval Pending From Reporting Manager"
                                    },
                                    fields=["name", "docstatus","from_date"])
        if leave_application:
            if employee.reports_to:
                    attendance_issues[employee.reports_to].append({
                        "employee_id": employee.name,
                        "employee_name": employee.employee_name,
                        "status": "Pending",
                    })

    for manager, employees in attendance_issues.items():
        send_consolidated_notification(manager, employees, today)

def send_consolidated_notification(manager, employees, date):
    manager_name = frappe.db.get_value("Employee", manager, "employee_name")
    manager_email = frappe.db.get_value("Employee", manager, "user_id")
    
    if not manager_email:
        frappe.log_error(f"No email found for manager {manager_name}", "Attendance Issues Notification")
        return
    
    subject = f"Leave Application Pending"
    
    # HTML message
    message = f"""
    <html>
    <head>
        <style>
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .missing {{
                color: red;
            }}
            .MO {{
                color: orange;
            }}
            .tableborder{{
                border:1px solid black;
                width:100%
            }}
            .tddata{{
                border: 1px solid black;
                text-align: left;
                padding: 1px;
            }}
        </style>
    </head>
    <body>
        <p>Dear {manager_name},</p>
        <p>Please Approve the Leave applications  for the following employees who reported to you</p>
        <table class='tableborder'>
            <tr>
                <th class='tddata'>Employee ID</th>
                <th class='tddata'>Employee Name</th>
                <th class='tddata'>Status</th>
                
            </tr>"""
    
    for employee in employees:
        status_class = "missing" if employee['status'] == "Absent" else "MO"
        message += f"""
            <tr>
                <td class='tddata'>{employee['employee_id']}</td>
                <td class='tddata'>{employee['employee_name']}</td>
                <td class='tddata {status_class}'>{employee['status']}</td>
                
            </tr>"""
    
    message += """
        </table>
        <p>Please ensure that these leave records are reviewed and updated as necessary for Payroll processing.</p>
        <p>Thank you for your attention to this matter.</p>
    </body>
    </html>"""
    
    # Send email notification
    frappe.sendmail(
        recipients=[manager_email],
        subject=subject,
        message=message,
        as_markdown=False
    )
    
    # Create a notification in Frappe
    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "for_user": manager_email,
        "type": "Alert",
        "document_type": "Attendance",
        "document_name": f"Attendance_Issues_{date}",
        "email_content": message
    }).insert(ignore_permissions=True)

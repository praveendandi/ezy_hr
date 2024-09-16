import frappe
from frappe.utils import today, add_days, getdate, time_diff_in_hours
from frappe.utils.background_jobs import enqueue
from collections import defaultdict

def get_email_footer():
    default_email_account = frappe.get_doc("Email Account", {"default_outgoing": 1})
    return default_email_account.footer

def send_checkins_notification():
    yesterday = add_days(today(), -1)
    employees = frappe.get_all("Employee", 
                               filters={"status": "Active", "name": ["not in", ["PRH-01", "PRH-12", "PRH-05", "PRH-03", "PRH-04"]]}, 
                               fields=["name", "employee_name", "user_id", "reports_to", "holiday_list"])
 
    attendance_issues = defaultdict(list)
 
    for employee in employees:
        if is_holiday_or_weekly_off(employee, yesterday):
            continue
        
        attendance = frappe.get_all("Attendance", 
                                    filters={
                                        "employee": employee.name,
                                        "attendance_date": yesterday,
                                        "docstatus": ["in", [0, 1]]  
                                    },
                                    fields=["name", "docstatus", "in_time", "out_time"])
    
        if not attendance:
            if employee.reports_to:
                attendance_issues[employee.reports_to].append({
                    "employee_id": employee.name,
                    "employee_name": employee.employee_name,
                    "status": "Absent",
                    "work_hours": 0
                })
        else:
            att = attendance[0]
            if att.docstatus == 0:
                work_hours = calculate_work_hours(att.in_time, att.out_time)
                if work_hours < 6:
                    if employee.reports_to:
                        attendance_issues[employee.reports_to].append({
                            "employee_id": employee.name,
                            "employee_name": employee.employee_name,
                            "status": "MO",
                            "work_hours": work_hours
                        })
    
    for manager, employees in attendance_issues.items():
        send_consolidated_notification(manager, employees, yesterday)
        for employee in employees:
            send_employee_notification(employee, yesterday)

def is_holiday_or_weekly_off(employee, date):
    if employee.holiday_list:
        holidays = frappe.get_all("Holiday", 
                                  filters={
                                      "holiday_date": date,
                                      "parent": employee.holiday_list
                                  }, 
                                  fields=["name"])
        if holidays:
            return True

    if employee.weekly_off and getdate(date).strftime("%A") == employee.weekly_off:
        return True

    return False

def calculate_work_hours(in_time, out_time):
    if in_time and out_time:
        return time_diff_in_hours(out_time, in_time)
    return 0
 
def send_consolidated_notification(manager, employees, date):
    manager_name = frappe.db.get_value("Employee", manager, "employee_name")
    manager_email = frappe.db.get_value("Employee", manager, "user_id")
    
    if not manager_email:
        frappe.log_error(f"No email found for manager {manager_name}", "Attendance Issues Notification")
        return
    
    subject = f"Missing Attendance Report for {date}"
    
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
        <p>Please review the attendance issues for the following employees who reported to you on {date}</p>
        <table class='tableborder'>
            <tr>
                <th class='tddata'>Employee ID</th>
                <th class='tddata'>Employee Name</th>
                <th class='tddata'>Status</th>
                <th class='tddata'>Work Hours</th>
            </tr>"""
    
    for employee in employees:
        status_class = "missing" if employee['status'] == "Absent" else "MO"
        message += f"""
            <tr>
                <td class='tddata'>{employee['employee_id']}</td>
                <td class='tddata'>{employee['employee_name']}</td>
                <td class='tddata {status_class}'>{employee['status']}</td>
                <td class='tddata'>{employee['work_hours']:.2f}</td>
            </tr>"""
    
    message += f"""
        </table>
        <p>Please ensure that these attendance records are reviewed and updated as necessary.</p>
        <p>Thank you for your attention to this matter.</p>
    </body>
    </html>"""
    
    frappe.sendmail(
        recipients=[manager_email],
        subject=subject,
        message=message,
        as_markdown=False  
    )
    
    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "for_user": manager_email,
        "type": "Alert",
        "document_type": "Attendance",
        "document_name": f"Attendance_Issues_{date}",
        "email_content": message
    }).insert(ignore_permissions=True)

def send_employee_notification(employee, date):
    employee_email = frappe.db.get_value("Employee", employee['employee_id'], "user_id")
    
    if not employee_email:
        frappe.log_error(f"No email found for employee {employee['employee_name']}", "Attendance Issues Notification")
        return
    
    subject = f"Your Attendance Report for {date}"
    
    message = f"""
    <html>
    <body>
        <p>Dear {employee['employee_name']},</p>
        <p>Your attendance not captured {date} punch is Missed:</p>
        <ul>
            <li>Status: {employee['status']}</li>
            <li>Work Hours: {employee['work_hours']:.2f}</li>
        </ul>
        <p>Please ensure that your attendance record is accurate. If there are any discrepancies, please update your attendance or contact your manager.</p>
    </body>
    </html>"""
    
    frappe.sendmail(
        recipients=[employee_email],
        subject=subject,
        message=message,
        as_markdown=False  
    )
    
    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": subject,
        "for_user": employee_email,
        "type": "Alert",
        "document_type": "Attendance",
        "document_name": f"Attendance_Issues_{employee['employee_id']}_{date}",
        "email_content": message
    }).insert(ignore_permissions=True)

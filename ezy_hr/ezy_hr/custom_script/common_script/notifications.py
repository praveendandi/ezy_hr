import frappe
from frappe.utils import today, add_days, getdate, time_diff_in_hours
from frappe.utils.background_jobs import enqueue
from collections import defaultdict


@frappe.whitelist()
def send_checkins_notification():
    yesterday = add_days(today(), -1)
    employees = frappe.get_all("Employee", 
                               filters={"status": "Active","name":["not in",["PRH-01","PRH-12","PRH-03","PRH-04","PRH-05"]]}, 
                               fields=["name", "employee_name", "user_id", "reports_to"])
 
    attendance_issues = defaultdict(list)
 
    for employee in employees:
        attendance = frappe.get_all("Attendance", 
                                    filters={
                                        "employee": employee.name,
                                        "attendance_date": yesterday,
                                        "docstatus": ["in", [0, 1]]  # Include draft (0) and submitted (1)
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
            if att.docstatus == 0:  # Draft
                work_hours = calculate_work_hours(att.in_time, att.out_time)
                if work_hours < 6:  # Assuming 8 hours is full day
                    attendance_issues[employee.reports_to].append({
                        "employee_id": employee.name,
                        "employee_name": employee.employee_name,
                        "status": "MO",
                        "work_hours": work_hours
                    })
 
    for manager, employees in attendance_issues.items():
        send_consolidated_notification(manager, employees, yesterday)
 
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
    
    # HTML message
    message = f"""
    <html>
    <head>
        <style>
        
            # table {{
            #     border-collapse: collapse;
            #     width: 100%;
            #     max-width: 800px;
            #     margin: 20px 0;
            # }}
            # th, td {{
            #     border: 1px solid #ddd;
            #     padding: 8px;
            #     text-align: left;
            # }}
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
    
    message += """
        </table>
        <p>Please ensure that these attendance records are reviewed and updated as necessary.</p>
        <p>Thank you for your attention to this matter.</p>
        <p>Sincerely,</p>

        <i>Paul Resorts & Hotels Pvt. Ltd.</i></p>
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

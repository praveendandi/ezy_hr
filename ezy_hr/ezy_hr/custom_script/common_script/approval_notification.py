import frappe 
from frappe.utils import today, add_days, getdate, time_diff_in_hours
from frappe.utils.background_jobs import enqueue
from collections import defaultdict
from datetime import date
from frappe.utils.data import (
    get_first_day
)

@frappe.whitelist()
def approval_notifications():
   
    today = date.today()
    
    final_data_leaves = defaultdict(list)
    approval_doctypes = frappe.db.get_list("Ezyhr Notification",['approval_doctype','fields','filters'])
    
    for doctype_details in approval_doctypes:
        doctype = doctype_details.get("approval_doctype")
        field = doctype_details.get("fields").split()
        filter = {key :["Between",["2024-08-25",today]] for key in doctype_details.get("filters").split()}
       
        filter.update({
            "workflow_state":"Approval Pending From Reporting Manager"
        })
       
        approval_doctypes = frappe.get_all(doctype, filters=filter,fields=field)
        
        
        if approval_doctypes:
            for each_record in approval_doctypes:
                reports_to_manager = frappe.get_doc("Employee",{"name":each_record.employee},["name","employee_name",'reports_to'])
                if reports_to_manager.reports_to:
                        final_data_leaves[reports_to_manager.reports_to].append({
                            "employee_id": reports_to_manager.name,
                            "employee_name": reports_to_manager.employee_name,
                            "status": "Pending",
                        })
       

        for manager, employees in final_data_leaves.items():
            send_consolidated_notification(manager, employees, today,doctype)


def send_consolidated_notification(manager, employees, date,doctype):
    manager_name,manager_email,salutation = frappe.db.get_value("Employee",manager,["employee_name","user_id","salutation"])
    if not manager_email:
        frappe.log_error(f"No email found for manager ",manager_name, "Attendance Issues Notification")
        return
    subject = f"Reminder: Pending Approval in HRMS"
    
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
        <p>Dear {salutation if salutation else ""} {manager_name},</p>
        <p>Kindly note, this is a gentle reminder that your approval is still pending in the HRMS approval section for {doctype}.
        We appreciate your prompt attention to this matter.</p>
        <table class='tableborder'>
            <tr>
                <th class='tddata'>Employee ID</th>
                <th class='tddata'>Employee Name</th>
                <th class='tddata'>Status</th>
                
            </tr>"""
    
    for employee in employees:
        message += f"""
            <tr>
                <td class='tddata'>{employee['employee_id']}</td>
                <td class='tddata'>{employee['employee_name']}</td>
                <td class='tddata'>{employee['status']}</td>
                
            </tr>"""
    
    message += """
        </table>
        <p>Kindly log into the HRMS portal [include link if necessary] and review the request as soon as possible to ensure timely processing.
        Your prompt attention to this matter is appreciated.</p>
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
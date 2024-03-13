import frappe
import json
import traceback
import sys


@frappe.whitelist()
def roster_update(data):
    try:
        row_data = json.loads(data)
        
        employee_id = frappe.db.sql(
            """
            SELECT 
            employee,employee_name,department
            FROM
            `tabEmployee`
            WHERE 
            department = %s
            And company = %s
            """,(row_data.get("department"),row_data.get('company')),
            as_dict = True
        )
        for each in employee_id:
            doc = frappe.get_doc(
                {
                    "doctype":"Shift Assignment",
                    "company":row_data.get('company'),
                    "employee":each.get("employee"),
                    "shift_type":row_data.get("shift_type"),
                    "start_date":row_data.get("start_date"),
                    "end_date":row_data.get("end_date"),
                    }
            )
            doc.docstatus = 1
            doc.insert()
        else:
            return {"success":True}
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "bulk_roster_update")

# @frappe.whitelist()
# def report_value():
#     from hrms.hr.doctype.shift_assignment.shift_assignment import get_events
    
#     row_data = get_events("2024-04-01 00:00:00","2024-04-30 00:00:00")
#     print(row_data,"poooooooooooooooo,,,,,,,,,,,,,,,,,,,,")
    
#     return row_data
    
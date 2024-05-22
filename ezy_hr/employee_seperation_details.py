import frappe
import erpnext
import json
import sys
import traceback


@frappe.whitelist()
def separation_details(data):
    try:
        row_data = json.loads(data) 
        employee_details = row_data.get("employees",None)
        
        final_result = []
        start_date = row_data.get("start_date")
        end_date = row_data.get("end_date")
        
        if employee_details:
            for each in employee_details:
                if frappe.db.exists("Employee Separation",{"employee":each.get("employee"),"boarding_status":("!=","Completed"),"boarding_begins_on":("between",(start_date,end_date))}):
                    doc = frappe.db.get_list("Employee Separation",
                                    {
                                        "employee":each.get("employee"),
                                        "boarding_begins_on":("between",(start_date,end_date)),
                                        "boarding_status":("!=","Completed")
                                        },
                                    ["name","employee","employee_name","department","designation","employee_separation_template","boarding_status"]
                                    )
                    for each in doc:
                        final_result.append(
                            each
                        )
                    
            return final_result
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "separation_details")

                
            

    
    
import frappe
import json
from frappe.utils import today, add_days
from frappe.utils import add_to_date
from datetime   import datetime 
# from frappe.model.mapper import get_mapped_doc

# @frappe.whitelist()
# def custom_api_for_make_employee_through_job_off(source_name, target_doc=None):
#     def set_missing_values(source, target):
#         target.personal_email, target.first_name = frappe.db.get_value(
#             "Job Applicant", source.job_applicant, ["email_id", "applicant_name"]
#         )

#     doc = get_mapped_doc(
#         "Job Offer",
#         source_name,
#         {
#             "Job Offer": {
#                 "doctype": "Employee",
#                 "field_map": {
#                     "applicant_name": "employee_name",
#                     "designation": "designation",
#                     "custom_department": "department",
#                     "offer_date": "scheduled_confirmation_date",
#                     "custom_level": "grade",
#                 }
#             },
#             "Salary Detail": {
#                 "doctype": "Salary Detail",
#                 "field_map": {
#                     "salary_component": "salary_component",
#                     # Add more field mappings as needed
#                 },
#                 "condition": lambda doc: doc.parentfield == "custom_earning",
#                 "add_if_empty": True,
#                 "postprocess": lambda source, target: target.update({"parentfield": "custom_earnings"})
#             },
#             "Salary Detail": {
#                 "doctype": "Salary Detail",
#                 "field_map": {
#                     "salary_component": "salary_component",
#                     # Add more field mappings as needed
#                 },
#                 "condition": lambda doc: doc.parentfield == "custom_deductions",
#                 "add_if_empty": True,
#                 "postprocess": lambda source, target: target.update({"parentfield": "custom_deductions"})
#             }
#         },
#         target_doc,
#         set_missing_values,
#     )
#     # frappe.logger("employee",allow)
#     return doc

@frappe.whitelist()
def assign_leave_policy(doc):
    try:
        row_data = json.loads(doc)
        if row_data.get("custom_leave_policy"):
            # Check if a Leave Policy Assignment already exists for this employee
            existing_assignment = frappe.get_all('Leave Policy Assignment', 
                                                filters={'employee': row_data.get("name")},
                                                fields=['name'])
            if existing_assignment:
                # Update the existing assignment
                leave_policy_assignment = frappe.get_doc('Leave Policy Assignment', existing_assignment[0]['name'])
            else:
                # Create a new assignment
                leave_policy_assignment = frappe.new_doc('Leave Policy Assignment')

            # Set the fields
            leave_policy_assignment.employee = row_data.get("name")
            leave_policy_assignment.leave_policy = row_data.get("custom_leave_policy")
            today = datetime.now().year
            current_year = today
            start_date = datetime(current_year, 1, 1)
            end_date = datetime(current_year, 12, 31)
            type_perid = "Leave Period"
            leave_policy_assignment.assignment_based_on = type_perid
            leave_period = frappe.db.get_list("Leave Period",filters={"company":row_data.get("company"),"from_date":start_date,"to_date":end_date},fields=["name"])
            
            leave_policy_assignment.leave_period = leave_period[0]['name']
        
            leave_policy_assignment.docstatus = 1

            leave_policy_assignment.save(ignore_permissions=True)

            return {"success":True}
        return {"success":False}
    
    except Exception as e:
        frappe.log_error(str(e))

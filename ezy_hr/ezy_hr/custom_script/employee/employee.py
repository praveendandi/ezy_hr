import frappe
import json
from frappe.utils import today, add_days,getdate,add_to_date
from datetime   import datetime 
import erpnext
import sys
import traceback
from frappe import _

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
def assign_leave_policy(doc,method=None):
    try:
        today = datetime.now().year
        current_year = today
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31)

        row_data = None
        if isinstance(doc,str):
           
            row_data = json.loads(doc)
        else:
            row_data = doc.as_dict()

        if not frappe.db.exists("Leave Period",{"company":row_data.get("company"),"from_date":start_date,"to_date":end_date}):
                return {"success":False,"reason":"Leave Period Is not Create Of {today}".format(today=today)}
    
        
        if row_data.get("custom_leave_policy"):

            # Check if a Leave Policy Assignment already exists for this employee
            existing_assignment = frappe.get_all('Leave Policy Assignment', 
                                                filters={'employee': row_data.get("name")},
                                                fields=['name'])
            if existing_assignment:
                # Update the existing assignment
                return {"success":False,"reason":"Leave Policy Assignment Already Assigned."}
            else:
                # Create a new assignment
                leave_policy_assignment = frappe.new_doc('Leave Policy Assignment')

                # Set the fields
                leave_policy_assignment.employee = row_data.get("name")
                leave_policy_assignment.leave_policy = row_data.get("custom_leave_policy")
                type_perid = "Leave Period"
                leave_policy_assignment.assignment_based_on = type_perid
                leave_period = frappe.db.get_list("Leave Period",filters={"company":row_data.get("company"),"from_date":start_date,"to_date":end_date},fields=["name"])
                
                leave_policy_assignment.leave_period = leave_period[0]['name']
            
                leave_policy_assignment.docstatus = 1

                leave_policy_assignment.save(ignore_permissions=True)

                return {"success":True,"reason":f"{'Leave policy assigned successfully'}"}
        return {"success":False,"reason":f"{'Failed to assign leave policy.'}"}
    
    except Exception as e:
        frappe.log_error(str(e))

def create_salary_structure_through_employee(doc, method=None):
   try:
       row_data = doc.as_dict()
       current_month, current_year = None, None

       if doc.custom_effective_date:
           change_date = getdate(doc.custom_effective_date)
           current_year = change_date.year
           current_month = change_date.month

           structure_name = f"{doc.name}-({current_month}-{current_year})"
           if not frappe.db.exists("Salary Structure", {"name": structure_name, "is_active": "Yes", "docstatus": 1}):
               create_salary_structure(doc, structure_name, row_data)
               update_gross_amount(doc)
           else:
               update_salary_structure(doc, current_year, current_month)
               update_gross_amount(doc)
               update_salary_assigement_value_or_base(doc,structure_name)
               
   except frappe.exceptions.DuplicateEntryError as e:
       frappe.log_error(f"Duplicate salary structure: {e}")
   except Exception as e:
       frappe.log_error(f"Error creating salary structure: {e}")
       
   if doc.status == "Active":
       if getattr(frappe.local, "handling_dynamic", False):
           return
       frappe.local.handling_dynamic = True
       try: 
          
           if not doc.user_id and (doc.custom_role and doc.prefered_email):
               user = create_employee_user(doc)
               if user:
                   employee_id = frappe.get_doc("Employee",doc.name)
                   role_profile_detail = frappe.get_doc("Role Profile",doc.custom_role)
                   employee_id.user_id = user.name
                   employee_id.create_user_permission =role_profile_detail.custom_create_user_permission
                   employee_id.save()
                   frappe.db.commit()
                   employee_id.reload()
               
           if not doc.leave_approver:
               employee_id = frappe.get_doc("Employee",doc.name)
               report_user_id = frappe.get_value("Employee", doc.reports_to, "user_id")
               employee_id.leave_approver = report_user_id
               employee_id.shift_request_approver = report_user_id
               frappe.db.commit()
               
           if doc.user_id and doc.custom_role:
               user_doc = frappe.get_doc("User", doc.user_id)
               if doc.custom_role != user_doc.role_profile_name:
                   user_doc.role_profile_name =  doc.custom_role
                   user_doc.save(ignore_permissions=True)
                   frappe.db.commit()
                   
                   employee_id = frappe.get_doc("Employee",doc.name)
                   role_profile_detail = frappe.get_doc("Role Profile",doc.custom_role)
                   employee_id.create_user_permission =role_profile_detail.custom_create_user_permission
                   if not role_profile_detail.custom_create_user_permission:
                        current_permissions = frappe.get_all(
                            "User Permission",
                            filters={'user': doc.user_id, 'allow': doc.doctype},
                            fields=['name', 'for_value'],
                            ignore_permissions=True
                            )
                        if current_permissions: 
                            frappe.delete_doc("User Permission", current_permissions[0].name,ignore_permissions=True)
                            
                   employee_id.user_id = doc.user_id
                   employee_id.save()
                   frappe.db.commit()
                   employee_id.reload()

                       
           if doc.custom_responsible_unit:
               current_permissions = frappe.get_all(
				"User Permission",
				filters={'user': doc.user_id, 'allow': 'Company'},
				fields=['name', 'for_value'],
				ignore_permissions=True
               )
               existing_units = [perm['for_value'] for perm in current_permissions]
               custom_list = [comp.as_dict().get("unit") for comp in doc.custom_responsible_unit]
               custom_list.append(doc.company)
               
               if set(existing_units) != set(custom_list):
                   for perm in current_permissions:
                       frappe.delete_doc("User Permission", perm['name'],ignore_permissions=True)
                   for unit in custom_list:
                       user_permission = frappe.new_doc('User Permission')
                       user_permission.update({
							"for_value": unit,
							"allow": "Company",
							"user": doc.user_id
						})
                       user_permission.insert(ignore_permissions=True)
                       frappe.db.commit()
                       
       except Exception as e:
           frappe.log_error(frappe.get_traceback(), 'handle_employee_save')
           frappe.db.rollback()
       finally:
           frappe.local.handling_dynamic = False

   elif doc.status == "Left":
       try:
           user_permissions = frappe.get_all("User Permission", filters={'user': doc.user_id}, fields=['name'],ignore_permissions=True)
           for perm in user_permissions:
               frappe.delete_doc("User Permission", perm['name'],ignore_permissions=True)
           doc.save()
           frappe.db.commit()
       except Exception as e:
           frappe.log_error(frappe.get_traceback(), 'handle_employee_status_update')
           frappe.db.rollback()

    
def create_salary_structure(doc, structure_name, row_data):
   earnings = []
   deductions = []
   for each_earn in row_data.get("custom_earnings", []):
       earnings.append({
           "doctype": "Salary Detail",
           "parent": structure_name,
           "parentfield": "earnings",
           "parenttype": "Salary Structure",
           "salary_component": each_earn.get("salary_component"),
           "abbr": each_earn.get("abbr"),
           "amount": each_earn.get("amount"),
       })

   for each_deduc in row_data.get("custom_deductions", []):
       deduction = {
           "doctype": "Salary Detail",
           "parent": structure_name,
           "parentfield": "deductions",
           "parenttype": "Salary Structure",
           "salary_component": each_deduc.get("salary_component"),
           "abbr": each_deduc.get("abbr"),
       }
       if each_deduc.get("amount_based_on_formula") and each_deduc.get("formula"):
           deduction.update({
               "condition": each_deduc.get("custom_employee_condition"),
               "amount_based_on_formula": 1,
               "formula": each_deduc.get("formula"),
               "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
           })
       else:
           deduction.update({
               "condition": each_deduc.get("custom_employee_condition"),
               "amount": each_deduc.get("amount"),
               "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
           })
       deductions.append(deduction)

   details = {
       "doctype": "Salary Structure",
       "name": structure_name,
       "company": doc.company or erpnext.get_default_company(),
       "earnings": earnings,
       "deductions": deductions,
       "payroll_frequency": "Monthly",
       "currency": "INR",
       "is_active": "Yes",
       "docstatus": 1
   }

   salary_structure_doc = frappe.get_doc(details)
   salary_structure_doc.insert()

   if salary_structure_doc.name and salary_structure_doc.docstatus == 1:
       salary_structure_assignment(doc, salary_structure_doc.name)

def salary_structure_assignment(doc, salary_structure):
   if not frappe.db.exists("Salary Structure Assignment",{"salary_structure":salary_structure,"from_date":doc.custom_effective_date,"docstatus":1}):
    def get_income_tax_slab():
        return frappe.db.get_value(
            'Income Tax Slab',
            filters={"name": ("like", ("%Old Tax%")), "disabled": 0, "company": doc.company or erpnext.get_default_company()},
            fieldname=['name']
        )

    assignment_details = {
        "doctype": "Salary Structure Assignment",
        "employee": doc.name,
        "salary_structure": salary_structure,
        "from_date": frappe.get_value("Employee", {"name": doc.name}, ['date_of_joining']) if not doc.custom_effective_date else doc.custom_effective_date,
        "income_tax_slab": doc.custom_income_tax_slab if doc.custom_income_tax_slab else get_income_tax_slab(),
        "docstatus": 1,
        "base": update_gross_amount(doc)
    }
    salary_structure_assig = frappe.get_doc(assignment_details)
    salary_structure_assig.insert()

def update_salary_structure(doc, current_year, current_month):
   custom_earnings_updates(doc, current_year, current_month)
   custom_deductions_updates(doc, current_year, current_month)
   
   salary_structure = f"{doc.name}-({current_month}-{current_year})"
   salary_structure_assignment(doc, salary_structure)

def update_salary_structure_details(structure_name, new_components, parentfield):
   previous_counts = frappe.db.count(
       "Salary Detail",
       filters={"parent": structure_name, "parentfield": parentfield, "docstatus": 1, "parenttype": "Salary Structure"}
   )

   previous_amount = frappe.db.sql("""
       SELECT SUM(sd.amount) as amount
       FROM `tabSalary Detail` as sd, `tabSalary Structure` as ss
       WHERE sd.parent = ss.name AND sd.parentfield = "earnings"
       AND ss.docstatus = 1 AND ss.name = %s
   """, (structure_name), as_list=1)[0][0]

   new_component_counts = len(new_components)
   new_component_amount = sum(each.get("amount", 0) for each in new_components)

   if new_component_counts != previous_counts or new_component_amount != previous_amount:
       frappe.db.delete(
           "Salary Detail",
           filters={"parent": structure_name, "parentfield": parentfield, "docstatus": 1, "parenttype": "Salary Structure"}
       )

       document = frappe.get_doc("Salary Structure", structure_name)
       for each_component in new_components:
           detail = {
               "doctype": "Salary Detail",
               "parent": structure_name,
               "parentfield": parentfield,
               "parenttype": "Salary Structure",
               "salary_component": each_component.get("salary_component"),
               "abbr": each_component.get("abbr"),
               "amount": each_component.get("amount"),
               "condition": each_component.get("custom_employee_condition"),
               "amount_based_on_formula": 1 if each_component.get("amount_based_on_formula") else 0,
               "formula": each_component.get("formula"),
               "do_not_include_in_total": 1 if each_component.get("do_not_include_in_total") else 0
           }
           child_doc = frappe.new_doc('Salary Detail')
           child_doc.update(detail)
           document.append(parentfield, child_doc)
       document.save()

def custom_earnings_updates(doc, current_year, current_month):
   new_row_data = doc.as_dict()
   new_components = new_row_data.get("custom_earnings", [])
   structure_name = f"{doc.name}-({current_month}-{current_year})"
   update_salary_structure_details(structure_name, new_components, "earnings")

def custom_deductions_updates(doc, current_year, current_month):
   new_row_data = doc.as_dict()
   new_components = new_row_data.get("custom_deductions", [])
   structure_name = f"{doc.name}-({current_month}-{current_year})"

   if new_components:
       update_salary_structure_details(structure_name, new_components, "deductions")
   else:
       is_change = False
       structure = frappe.get_doc("Salary Structure", structure_name)
       for each in structure.deductions:
           frappe.db.delete("Salary Detail", {"name": each.name, "parentfield": "deductions", "docstatus": 1, "parenttype": "Salary Structure"})
           is_change = True

       if is_change:
           structure.save()

def update_gross_amount(doc):
   new_row_data = doc.as_dict()
   if len(new_row_data.get("custom_earnings",[])) >0:
       new_component_amount = sum(each.get("amount", 0) for each in new_row_data.get("custom_earnings", []))
       frappe.db.set_value("Employee",{"name":new_row_data.get("name")},{"custom_gross_amount":new_component_amount})
       frappe.db.commit()
       return new_component_amount

def update_salary_assigement_value_or_base(doc,structure_name):
   new_row_data = doc.as_dict()
   if len(new_row_data.get("custom_earnings",[])) >0:
       new_component_amount = sum(each.get("amount", 0) for each in new_row_data.get("custom_earnings", []))
       frappe.db.set_value("Salary Structure Assignment",{"salary_structure":structure_name,"from_date":doc.custom_effective_date},{"base":new_component_amount})
       frappe.db.commit()

def update_and_create_salary(self, method=None):
   try:
       if self.custom_effective_date:
           employee_details = frappe.get_doc("Employee", self.employee)

           employee_details.set('custom_earnings', [])

           for each in self.custom_earnings_detail:
               employee_details.append("custom_earnings", {
                   "salary_component": each.get("salary_component"),
                   "amount": each.get("new_amount"),
               })

           employee_details.custom_effective_date = self.custom_effective_date
           employee_details.custom_gross_amount = self.custom_new_gross_amount
           employee_details.save(ignore_permissions=True)
           frappe.db.commit()

   except Exception as e:
       frappe.log_error(f"Update And Create Salary: {str(e)}")

def check_effective_date(doc, method=None):

   if doc.custom_effective_date:
       effective_date = getdate(doc.custom_effective_date)
       previous_effective_date = getdate(doc.custom_previous_effective_date)

       if effective_date <= previous_effective_date:
           frappe.throw("Please check the Effective Date. It should not be earlier than the previous effective date.")


@frappe.whitelist()
def update_employee_biometric_id(doc, method=None):
   try:
       if not doc.attendance_device_id:
           employee_id = doc.name.replace('-', '')
           doc.attendance_device_id = employee_id
           print(f'Employee ID {employee_id} set as Attendance Device ID')
   except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Employee Checkin Details")

@frappe.whitelist()
def create_employee_user(doc):
   if not frappe.db.exists("User", doc.prefered_email):
       user = frappe.new_doc('User')
       user.update({
			'doctype': 'User',
			'email': doc.prefered_email,
			'first_name': doc.first_name,
			'last_name': doc.last_name,
			'send_welcome_email': 0,
			"role_profile_name": doc.custom_role,
			"username": doc.name
		})
       user.insert(ignore_permissions=True)
       return user
   return frappe.get_doc("User",doc.prefered_email)

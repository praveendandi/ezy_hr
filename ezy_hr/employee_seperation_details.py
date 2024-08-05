import frappe
import json
import sys
import traceback
from datetime import datetime, timedelta

@frappe.whitelist()
def separation_details(data):
   try:
       row_data = json.loads(data)
       employee_details = row_data.get("employees", None)
       start_date = row_data.get("start_date")
       end_date = row_data.get("end_date")

       if employee_details:
           for each in employee_details:
               if frappe.db.exists("Employee Separation", {
                   "employee": each.get("employee"),
                   "boarding_status": ("!=", "Completed"),
                   "boarding_begins_on": ("between", (start_date, end_date))
               }):
                   doc = frappe.db.get_list("Employee Separation",
                                            {
                                                "employee": each.get("employee"),
                                                "boarding_begins_on": ("between", (start_date, end_date)),
                                                "boarding_status": ("!=", "Completed")
                                            },
                                            ["name", "employee", "employee_name", "department", "designation", "employee_separation_template", "boarding_status"]
                                            )
                   if doc:
                       each.update({
                           "custom_separation_id": doc[0]['name'],
                           "custom_status": doc[0]['boarding_status']
                       })
           return employee_details
   except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "separation_details")

@frappe.whitelist()
def separation_activity_update(data):
   try:
       row_data = data.as_dict()
       doc = frappe.get_doc("Employee Separation", row_data.get('name'))

       for each_record in doc.activities:
           if each_record.get("custom_status"):
               task_name = each_record.get('task')
               if frappe.db.exists("Task", {"name": task_name, "status": ('!=', "Completed")}):
                   get_task = frappe.get_doc("Task", task_name)
                   get_task.status = "Completed"
                   get_task.completed_on = datetime.now()
                   get_task.save()
                   frappe.db.commit()

   except Exception as e:
       exc_type, exc_obj, exc_tb = sys.exc_info()
       frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "separation_activity_update")

@frappe.whitelist()
def fetch_employees_with_upcoming_relieving():
   try:
           
       exit_days = frappe.get_single('EzyHr Settings')
       exit_begins_on = exit_days.exit_begins_on
       today = datetime.today().date()
       relieving_date_cutoff = today + timedelta(days=exit_begins_on) 

       employees = frappe.db.get_list(
           "Employee",
           filters={"relieving_date": ["<=", relieving_date_cutoff], "status": "Active"},
           fields=["name", "employee_name", "relieving_date", "resignation_letter_date", "department"]
       )

       for emp in employees:
           if not is_employee_separation_record_exists(emp.get("name")):
               create_employee_separation_record(emp)

       return "Employee separation records created successfully."
   
   except Exception as e:
       frappe.log_error(f"Error: {str(e)}", "fetch_employees_with_upcoming_relieving")
       return f"Error: {str(e)}"


def is_employee_separation_record_exists(employee_name):
   existing_record = frappe.db.exists("Employee Separation", {"employee": employee_name})
   return bool(existing_record)

def get_last_updated_template():
   last_template = frappe.get_all(
       "Employee Separation Template",
       order_by="modified desc",
       limit=1
   )
   return last_template[0] if last_template else None

def create_employee_separation_record(employee):
   last_template = get_last_updated_template()

   if not last_template:
       frappe.throw("No Employee Separation Template found")

   template_doc = frappe.get_doc("Employee Separation Template", last_template.name)

   separation_doc = frappe.new_doc("Employee Separation")
   separation_doc.employee = employee.get("name")
   separation_doc.employee_name = employee.get("employee_name")
   separation_doc.relieving_date = employee.get("relieving_date")
   separation_doc.resignation_letter_date = employee.get("resignation_letter_date")
   separation_doc.department = employee.get("department")
   separation_doc.boarding_begins_on = employee.get("resignation_letter_date")
   separation_doc.employee_separation_template = template_doc.name
   
   separation_doc.activities = template_doc.activities
   separation_doc.notify_users_by_email = 1

   if template_doc.get("employee_boarding_activity"):
       for activity in template_doc.get("employee_boarding_activity"):
           separation_doc.append("employee_boarding_activity", {
               "activity_name": activity.activity_name,
               "activity_date": activity.activity_date,
               "status": activity.status
           })
   
   separation_doc.save(ignore_permissions=True)
   frappe.db.commit()

   separation_doc.submit()

   return separation_doc



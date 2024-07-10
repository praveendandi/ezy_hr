# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from hrms.hr.utils import update_employee_work_history

class EmployeeFieldsUpdate(Document):
    
    def on_submit(self):
        employee = frappe.get_doc("Employee", self.employee_id)
        
        employee = update_employee_work_history(
            employee, self.employee_property, date=self.creation_date
        )
        employee.save()
        
    def on_cancel(self):
        employee = frappe.get_doc("Employee", self.employee_id)
                
        employee = update_employee_work_history(
            employee, self.employee_property, date=self.creation_date, cancel=True
        )
        employee.save()


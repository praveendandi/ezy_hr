# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import erpnext
import sys
import traceback
from frappe.utils import getdate


class EmployeeSalaryUpdate(Document):

    def on_submit(self):
        
        self.update_and_create_salary()

    def update_and_create_salary(self):
        try:
            if self.new_effective_date:
                employee_details = frappe.get_doc("Employee", self.employee_id)
            
                employee_details.set('custom_earnings', [])
            
                for each in self.component_detail:
                    employee_details.append("custom_earnings", {
                        "salary_component": each.get("salary_component"),
                        "amount": each.get("new_amount"),
                    })
                    
                employee_details.custom_effective_date = self.new_effective_date
                # employee_details.custom_gross_amount = self.custom_new_gross_amount

                employee_details.save(ignore_permissions=True)
                frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Update And Create Salary: {str(e)}")


@frappe.whitelist()
def update_earning_table(data):
    
    try:
        row_data = json.loads(data) 
        
        employee_id = row_data.get("employee_id") or row_data.get("employee")

        get_salary_detail = frappe.db.sql("""
            SELECT salary_component, amount, abbr
            FROM `tabSalary Detail`
            WHERE parent = %s
            AND parentfield = %s
            AND parenttype = %s
            ORDER BY idx ASC
        """, (employee_id, 'custom_earnings', 'Employee'), as_dict=True)

        return get_salary_detail
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "update_earning_table")





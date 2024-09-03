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

    def validate(self):
        
        self.check_effective_date()
    
    def on_submit(self):
        
        self.update_and_create_salary()

    def update_and_create_salary(self):
        try:
            if self.new_effective_date:
                employee_details = frappe.get_doc("Employee", self.employee_id)
            
                employee_details.set('custom_earnings', [])
                employee_details.set('custom_deductions', [])
            
                for each in self.component_detail:
                    employee_details.append("custom_earnings", {
                        "salary_component": each.get("salary_component"),
                        "amount": each.get("new_amount"),
                    })
                
                for each_ded in self.deduction_detail:
                    employee_details.append("custom_deductions", {
                        "salary_component": each_ded.get("salary_component"),
                        "amount": each_ded.get("amount"),
                        "custom_employee_condition":each_ded.get("custom_employee_condition"),
                        "condition": each_ded.get("condition"),
                        "amount_based_on_formula": 1 if each_ded.get("amount_based_on_formula") else 0,
                        "formula": each_ded.get("formula"),
                        "do_not_include_in_total": 1 if each_ded.get("do_not_include_in_total") else 0
                    })
                    
                employee_details.custom_effective_date = self.new_effective_date
                # employee_details.custom_gross_amount = self.custom_new_gross_amount

                employee_details.save(ignore_permissions=True)
                frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Update And Create Salary: {str(e)}")
            
    def check_effective_date(self):
        # Old Employee validatation
        if self.new_effective_date and self.previous_review_date:
            effective_date = getdate(self.new_effective_date)
            previous_effective_date = getdate(self.previous_review_date)
            date_of_joining = getdate(self.date_of_joining)
            
            if effective_date <= previous_effective_date:
                frappe.throw("Please check the Effective Date. It should not be earlier than the previous effective date....")
                
        # New Employee validatation
        if self.new_effective_date and self.date_of_joining:
            effective_date = getdate(self.new_effective_date)
            date_of_joining = getdate(self.date_of_joining)
            
            if effective_date < date_of_joining:
                frappe.throw("You Assign Before Joining Date of Employee.....")


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

@frappe.whitelist()
def update_deduction_table(data):
    try:
        row_data = json.loads(data) 
        employee_id = row_data.get("employee_id") or row_data.get("employee")
        employee_docs = frappe.get_list("Employee",filters={ "name": ["not like", "%-T%"],"employee": employee_id},fields=["name", "employee_name", "employee","company"])
        if employee_docs:
            get_deduction_detail = frappe.db.sql("""
                SELECT sd.*
                FROM `tabSalary Detail` sd
                JOIN `tabEzy Deductions Formula` ezyd ON sd.parent = ezyd.name
                WHERE ezyd.unit = %s
                AND sd.parentfield = %s
                AND sd.parenttype = %s
                ORDER BY sd.idx ASC
                """, (employee_docs[0].get("company"), 'deductions', 'Ezy Deductions Formula'), as_dict=True
            )

            return get_deduction_detail
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "update_deduction_table")



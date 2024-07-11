import frappe
import erpnext
import sys
import traceback
from datetime import datetime
from frappe.utils import getdate

# This function work on employee promotion after submit doc
@frappe.whitelist()
# def test():
#     frappe.errprint("QWERTYU")
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

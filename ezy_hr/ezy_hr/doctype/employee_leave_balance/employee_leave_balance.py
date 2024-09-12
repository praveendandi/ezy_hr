# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class EmployeeLeaveBalance(Document):

    def after_insert(self):
        self.update_current_leave_balance()

    def on_update(self):
        self.update_current_leave_balance()

    def update_current_leave_balance(self):
        leave_balance_on = self.leave_balance_on
        leave_balance_updated = self.leave_balance_updated
        allocate_frequency = self.allocate_frequency
        allocated_count = self.allocated_count  

        if not leave_balance_on or not leave_balance_updated:
            frappe.throw("Both 'Leave Balance Given On' and 'Leave Balance Upto Today' fields must be set.")
            return

        if isinstance(leave_balance_on, str):
            start_date = datetime.strptime(leave_balance_on, '%Y-%m-%d')
        else:
            start_date = leave_balance_on

        if isinstance(leave_balance_updated, str):
            end_date = datetime.strptime(leave_balance_updated, '%Y-%m-%d')
        else:
            end_date = leave_balance_updated

        delta_days = (end_date - start_date).days

        if allocate_frequency == 'Monthly':
            frequency_days = 30
        elif allocate_frequency == 'Quarterly':
            frequency_days = 90
        elif allocate_frequency == 'Half Yearly':
            frequency_days = 182  
        elif allocate_frequency == 'Yearly':
            frequency_days = 365
        else:
            frequency_days = 1 
        
        leave_count = (delta_days // frequency_days) * allocated_count

        self.db_set('leave_balance_updated', datetime.today().strftime('%Y-%m-%d'))
        self.db_set('current_leave_balance', self.leave_balance + leave_count)

def update_all_leave_balances():
    leave_balances = frappe.get_all("Employee Leave Balance", fields=["name"])

    for lb in leave_balances:
        leave_balance_doc = frappe.get_doc("Employee Leave Balance", lb.name)
        leave_balance_doc.update_current_leave_balance()

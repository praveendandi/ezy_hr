# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EmployeeMissingCheckinsRequest(Document):
    def on_submit(self):
        # Fetching existing Employee Missing Checkins Requests for the current employee
        existing_requests = frappe.db.get_all("Employee Missing Checkins Request",
                                               filters={"employee": self.employee},
                                               fields=["employee", "employee_name", "date", "in_time", "out_time", "status"])
        # Printing the fetched requests
        print(existing_requests, '///////////////////////////////get_employee_checkin_requests')
        if self.docstatus == 1:
            # Set log_type based on the presence of out_time
            if self.out_time:
                log_type = "OUT"
            else:
                log_type = "IN"

            doc = frappe.get_doc({
                'doctype': 'Employee Checkin',
                'employee': self.employee,
                'employee_name': self.employee_name,
                'time': self.out_time,
                'log_type': log_type,  
                'custom_correction': "Manual"
            })
            doc.insert(ignore_permissions=True)

        

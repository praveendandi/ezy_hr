# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import erpnext
import sys
import traceback

class EmployeeSalaryUpdate(Document):
    pass


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

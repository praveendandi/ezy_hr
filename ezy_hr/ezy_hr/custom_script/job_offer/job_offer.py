import frappe
from frappe.model.document import Document
import json
import erpnext
import sys
import traceback
from frappe.utils import getdate


@frappe.whitelist()
def update_deduction_table(data):
    try:
        row_data = json.loads(data)
        
        if row_data.get("company"):
            get_deduction_detail = frappe.db.sql("""
                SELECT sd.*
                FROM `tabSalary Detail` sd
                JOIN `tabEzy Deductions Formula` ezyd ON sd.parent = ezyd.name
                WHERE ezyd.unit = %s
                AND sd.parentfield = %s
                AND sd.parenttype = %s
                ORDER BY sd.idx ASC
                """, (row_data.get("company"), 'deductions', 'Ezy Deductions Formula'), as_dict=True
            )
            
            return get_deduction_detail
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "update_deduction_table")



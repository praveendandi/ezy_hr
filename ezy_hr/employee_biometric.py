import frappe
import erpnext
import sys
import traceback

@frappe.whitelist()
def update_employee_biometric_id(doc, method=None):
    try:

        # Check if the attendance_device_id is already set
        if not doc.attendance_device_id:
            # Remove hyphens from employee_id
            employee_id = doc.name.replace('-', '')
            
            # Set attendance_device_id to the cleaned employee_id
            doc.attendance_device_id = employee_id
            print(f'Employee ID {employee_id} set as Attendance Device ID')
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Employee Checkin Details")

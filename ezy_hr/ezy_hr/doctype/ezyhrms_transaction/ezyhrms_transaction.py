# Copyright (c) 2024, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import sys
import traceback
import pandas as pd
from hrms.hr.doctype.employee_checkin.employee_checkin import add_log_based_on_employee_field
from datetime import datetime

class EzyHrmsTransaction(Document):
    def after_insert(self):
        if self.terminal_alias.lower() == "out":
            self.in_out = "OUT"
        elif self.terminal_alias.lower() == "in":
            self.in_out = "IN"
        
        if "App" in self.terminal_sn and int(self.punch_state) == 1:
            self.in_out = "OUT"
        elif "App" in self.terminal_sn and int(self.punch_state) == 0:
            self.in_out = "IN"

        if "App" in self.terminal_sn:
            self.terminal_alias = "App"
        
        check_in_date = self.punch_time
        device_info = frappe.get_value("Biometric Devices", {'device_id': self.terminal_sn}, ['device_type'])
        if device_info:
            if device_info == "In & Out":
                emp_id = frappe.db.get_value(
                "Employee",
                    filters={'attendance_device_id': self.emp_code},
                    fieldname='name'
                )
                # Update
                if isinstance(self.punch_time,str):
                    datetime_obj = datetime.strptime(self.punch_time,"%Y-%m-%d %H:%M:%S").replace(hour=0,minute=0,second=0)
                    check_in_date = datetime_obj
                else:
                    check_in_date = self.punch_time

                date_in_out = check_in_date.date()
                first_punch = frappe.get_list("Employee Checkin",filters={"employee":emp_id,"time":['Between',[date_in_out,date_in_out]]},fields=['log_type','time'],order_by="time desc",limit=1)
                
                if len(first_punch) <=0:
                    self.in_out = "IN"
                else:
                    if first_punch[0].get('log_type') == "IN":
                        self.in_out = "OUT"
                    if first_punch[0].get("log_type") == "OUT":
                        self.in_out = "IN"
        
        try:
            add_log_based_on_employee_field(employee_field_value = self.emp_code,timestamp=self.punch_time,device_id=self.terminal_alias,log_type=self.in_out)

        except Exception as e:
            if not "This employee already has a log with the same timestamp" in str(e):
                doctype = {"doctype":"EzyHrms Failed Records"}
                required_fields = {"id":self.id,"emp_code":self.emp_code,"punch_time":self.punch_time,"punch_state":self.punch_state,"verify_type":self.verify_type,
                        "work_code":self.work_code,"terminal_sn":self.terminal_sn,"terminal_alias":self.terminal_alias,"area_alias":self.area_alias,"longitude":self.longitude,
                        "latitude":self.latitude,"source":self.source,"purpose":self.purpose,"crc":self.crc,"is_attendance":self.is_attendance,"upload_time":self.upload_time,
                        "sync_status":self.sync_status,"emp_id":self.emp_id,"terminal_id":self.terminal_id,"company_id":self.company_id,"in_out":self.in_out}
                doctype.update(required_fields)
                error_message = {"error_message":f"{str(e)}"}
                doctype.update(error_message)
                inserting_failed_log = frappe.get_doc(doctype)
                inserting_failed_log.insert(ignore_permissions=True)
                frappe.db.commit()
                exc_type, exc_obj, exc_tb = sys.exc_info()
                frappe.log_error("Sync Error in EzyHrms", "line No:{}\n{}".format(
                    exc_tb.tb_lineno, traceback.format_exc()))
            else:
                pass
  

@frappe.whitelist()
def sync_transaction_month_wise(list_of_ids):
    # pass list of ids of records as parameter
    import ast
    try:
        if isinstance(list_of_ids,str):
            list_of_ids=ast.literal_eval(list_of_ids)
        if len(list_of_ids)<=0:
            return {"success":False,"message":"Select atleast one record for syncing data."}
        
        cleanedList = [x for x in list_of_ids if str(x) != 'nan']
        cleanedList = list(filter(None, cleanedList))
        cleanedList = tuple(cleanedList)
        
        transaction_rows = frappe.db.get_list("EzyHrms Transaction", filters={"name":["in",list_of_ids]}, fields =["*"])  #"punch_time","emp_code","terminal_alias","terminal_sn","punch_state"
        
        transaction_cols = pd.DataFrame.from_records(transaction_rows)
        transaction_cols['in_out'] = transaction_cols.apply(lambda x : "OUT" if "out" in str(x["terminal_alias"]).lower() else "IN" if "in" in str(x["terminal_alias"]).lower() else x["terminal_alias"],axis=1)
        transaction_cols['in_out'] = transaction_cols.apply(lambda x : ("OUT" if ("App" in str(x["terminal_sn"]) and int(x['punch_state'])==1) else "IN" if ("App" in str(x["terminal_sn"]) and int(x['punch_state'])==0) else x["in_out"]),axis=1)
        transaction_cols['terminal_alias'] = transaction_cols.apply(lambda x: 'App' if "App" in str(x["terminal_sn"]) else x['terminal_alias'],axis=1)
        
        # transaction_cols = transaction_cols[['emp_code','punch_time','terminal_alias','in_out']]
        dict_of_trx_records = transaction_cols.to_dict("records")
        
        for i in range(0,len(dict_of_trx_records)):
            data = dict_of_trx_records[i]
   
            # employee = frappe.db.get_values(
            # 	"Employee",
            # 	{"attendance_device_id": data['emp_code']},
            # 	["name", "employee_name", "attendance_device_id"],
            # 	as_dict=True,
            # )
            # if employee:
            # 	employee = employee[0]
            
            # 	payload = {
            # 		'employee' :employee.name,
            # 		"employee_name":employee.employee_name,
            # 		'time' : data['punch_time'].__str__(),
            # 		'device_id' : data['terminal_alias'],
            # 		'log_type' : data['in_out']
            # 	}
            try:
                # if not frappe.db.exists("Employee Checkin", payload):
                add_log_based_on_employee_field(employee_field_value = data['emp_code'],timestamp=data['punch_time'],device_id=data["terminal_alias"],log_type=data['in_out'])
            
            except Exception as e:
                if not "This employee already has a log with the same timestamp" in str(e):
                    doctype = {"doctype":"EzyHrms Failed Records"}
                    doctype.update(data)
                    error_message = {"error_message":f"{str(e)}"}
                    doctype.update(error_message)
                    inserting_failed_log = frappe.get_doc(doctype)
                    inserting_failed_log.insert(ignore_permissions=True)
                    frappe.db.commit()
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    frappe.log_error("Sync Error in EzyHrms", "line No:{}\n{}".format(
                        exc_tb.tb_lineno, traceback.format_exc()))
                else:
                    continue
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("Sync Error in EzyHrms", "line No:{}\n{}".format(
            exc_tb.tb_lineno, traceback.format_exc()))
        return {"success": False, "error": str(e)}





@frappe.whitelist()
def get_checkin_alert():
    try:
        
        # Get the latest document in EzyHrms Transaction
        get_latest = frappe.get_last_doc('EzyHrms Transaction')
        
        get_doc_detail = frappe.get_doc("EzyHrms Transaction", {"name": get_latest.name})
        
        # Calculate the duration between the current time and the creation of the last document
        current_time = datetime.now()
        doc_creation = get_doc_detail.creation
        duration = current_time - doc_creation
        hours = duration.total_seconds() // 3600
        
        
        
        # Get email details from EzyHrms Maintenance
        get_recipient_details = frappe.get_last_doc('EzyHrms Maintenance')
        recipients_details = frappe.get_doc("EzyHrms Maintenance", {"name": get_recipient_details.name})
        
        recipients = recipients_details.receipts.split(",") if recipients_details.receipts else None
        subject = recipients_details.subject
        message = recipients_details.message
        
        # Log email information
        frappe.logger().info(f"Recipients: {recipients}, Subject: {subject}")
        
        # Send email if the last record was created more than 6 hours ago
        if hours >= 6:
            email_args = {
                "recipients": recipients,
                "subject": subject,
                "message": message,
                "now": True
            }
            frappe.sendmail(**email_args)
        else:
            frappe.logger().info("No email sent. Condition not met.")
        
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("EzyHrms Transaction Fail", "Line No: {}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()))
        frappe.logger().error(f"Error: {str(e)}")

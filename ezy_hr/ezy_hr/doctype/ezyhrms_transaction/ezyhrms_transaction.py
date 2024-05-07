# Copyright (c) 2024, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import sys
import traceback
import pandas as pd
from hrms.hr.doctype.employee_checkin.employee_checkin import add_log_based_on_employee_field

class EzyHrmsTransaction(Document):
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
   
			employee = frappe.db.get_values(
				"Employee",
				{"attendance_device_id": data['emp_code']},
				["name", "employee_name", "attendance_device_id"],
				as_dict=True,
			)
			if employee:
				employee = employee[0]
			
				payload = {
					'employee' :employee.name,
					"employee_name":employee.employee_name,
					'time' : data['punch_time'].__str__(),
					'device_id' : data['terminal_alias'],
					'log_type' : data['in_out']
				}
			
			try:
				if not frappe.db.exists("Employee Checkin", payload):
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
					pass
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Sync Error in EzyHrms", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}
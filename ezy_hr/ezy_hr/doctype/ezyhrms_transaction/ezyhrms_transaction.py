# Copyright (c) 2024, caratred and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import sys
import traceback
import pandas as pd
from hrms.hr.doctype.employee_checkin.employee_checkin import add_log_based_on_employee_field

class EzyHrmsTransaction(Document):
	def after_insert(self):    
		# response = add_log_based_on_employee_field(self.emp_code,self.punch_time,self.terminal_alias,self.in_out)
		# if "frappe.exceptions.ValidationError: This employee already has a log with the same timestamp" in response["exception"]:
		# 	print(f'{data["employee_field_value"]} already has a log with same timestamp {data['punch_time'].__str__()} ----- is a duplicate log','\n')
		# elif "'employee_field_value' and 'timestamp' are required." in response['exception']:
		# 	# data = dict_of_trx_records[i]
		# 	data['error_message'] = "'employee_field_value' and 'timestamp' are required."
		# 	# response = requests.post(f"{config_file.FRAPPE_URL}/api/resource/EzyHrms Transaction", headers=headers, data=data)
		# 	# if response.status_code!=200:
		# 	# 	return {'success':False,'message':"""Might be Permission issue for particular doctype 'EzyHrms Transaction' else Server is down in Frappe 15."""}

		# elif 'No Employee found for the given employee field value.' in response['exception']:
		# 	data = dict_of_trx_records[i]
		# 	data['error_message'] = f"""No Employee found for the given employee field value.---- 'attendance_device_id':'{data["emp_code"]}'"""
		# 	response = requests.post(f"{config_file.FRAPPE_URL}/api/resource/EzyHrms Transaction", headers=headers, data=data)
		# 	if response.status_code!=200:
		# 		return {'success':False,'message':"""Might be Permission issue for particular doctype 'EzyHrms Transaction' else Server is down in Frappe 15."""}
            


	# def after_insert(self):
		frappe.client.set_value("EzyHrms Last ID","EzyHrms Last ID","last_id",int(self.id)+1)
		frappe.db.commit()
	


@frappe.whitelist()
def sync_transaction_month_wise(list_of_ids: list|None):
	# pass list of ids of records as parameter
	try:
		if len(list_of_ids)<=0:
			return {"success":False,"message":"Select atleast one record for syncing data."}
		
		cleanedList = [x for x in list_of_ids if str(x) != 'nan']
		cleanedList = list(filter(None, cleanedList))
		cleanedList = tuple(cleanedList)
		
		transaction_rows = frappe.db.get_list("EzyHrms Transaction", filters={"name":["in",list_of_ids]}, fields =["punch_time","emp_code","terminal_alias","terminal_sn","punch_state"])
		
		transaction_cols = pd.DataFrame.from_records(transaction_rows)
		transaction_cols['in_out'] = transaction_cols.apply(lambda x : "OUT" if "out" in str(x["terminal_alias"]).lower() else "IN" if "in" in str(x["terminal_alias"]).lower() else x["terminal_alias"],axis=1)
		transaction_cols['in_out'] = transaction_cols.apply(lambda x : ("OUT" if ("App" in str(x["terminal_sn"]) and int(x['punch_state'])==1) else "IN" if ("App" in str(x["terminal_sn"]) and int(x['punch_state'])==0) else x["in_out"]),axis=1)
		transaction_cols['terminal_alias'] = transaction_cols.apply(lambda x: 'App' if "App" in str(x["terminal_sn"]) else x['terminal_alias'],axis=1)
		
		transaction_cols = transaction_cols[['emp_code','punch_time','terminal_alias','in_out']]

		dict_of_trx_records = transaction_cols.to_dict("records")
		
		for i in range(0,len(dict_of_trx_records)):
			data = dict_of_trx_records[i]
			data = {
				'employee_field_value' : data['emp_code'],
				'timestamp' : data['punch_time'].__str__(),
				'device_id' : data['terminal_alias'],
				'log_type' : data['in_out']
			}
			
			add_log_based_on_employee_field(data)
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("Sync Error in EzyHrms", "line No:{}\n{}".format(
			exc_tb.tb_lineno, traceback.format_exc()))
		return {"success": False, "error": str(e)}
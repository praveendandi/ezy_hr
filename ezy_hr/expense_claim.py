import frappe
import erpnext
import sys
import traceback
import json


@frappe.whitelist()
def get_travel_request(doc):
    
    try:
        row_data = json.loads(doc)
        
        costing_child = row_data.get("costings")
        
        travel_details = row_data.get("itinerary")
        
        return costing_child
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "get_travel_request")

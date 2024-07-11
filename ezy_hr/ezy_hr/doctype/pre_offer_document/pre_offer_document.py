# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
import sys
import traceback
from frappe.model.document import Document


class PreOfferDocument(Document):
	pass


def creating_pre_offer_document(doc,method=None):
    try:
        if frappe.db.exists("Personal file Check list",{"aadhar_no":doc.aadhar_no}):
            
            if doc.current_ctc_structure:
                frappe.db.set_value("Personal file Check list",{"aadhar_no":doc.aadhar_no},{
                    "current_ctc_structure":1
                })
                
            if doc.first_slip and doc.second_slip and doc.third_slip:
                frappe.db.set_value("Personal file Check list",{"aadhar_no":doc.aadhar_no},{
                    "payslips_of_last_three_months":1
                })
                
            frappe.db.commit()
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "creating_pre_offer_document")


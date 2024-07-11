# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt
from frappe.model.document import Document
import frappe
import sys
import traceback


class Prejoiningdocument(Document):
	pass
def creating_new_pre_joining_document(doc,mothod):
    try:
        if frappe.db.exists("Personal file Check list",{"aadhar_no":doc.aadhar_no}):
            frappe.db.set_value("Personal file Check list",{"aadhar_no":doc.aadhar_no},
                                {
                                    "image": 1 if doc.image else 0,
                                    "dob_proof":1 if doc.dob_proof else 0,
                                    "educational_and_professional":1 if doc.educational_and_professional else 0,
                                    "employment_certificate":1 if doc.employment_certificate else 0,
                                    "form_16_12ba":1 if doc.form_16_12ba else 0,
                                    "id_proof_and_address":1 if doc.id_proof_and_address else 0,
                                    "pan_card":1 if doc.pan_card else 0,
                                    "aadhar_card":1 if doc.aadhar_card else 0,
                                })
            
            frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "creating_new_pre_joining_document")

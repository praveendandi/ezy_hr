import frappe
import sys
import traceback


def new_job_condidate_application(doc,mothod=None):
    try:
        if not frappe.db.exists("Personal file Check list",{"aadhar_no":doc.custom_aadhar_no}):
            
            new_doc = frappe.get_doc({
                "doctype":"Personal file Check list",
                "job_applicant_email":doc.email_id,
                "applicant_name":doc.applicant_name,
                "aadhar_no":doc.custom_aadhar_no,
                "unit":doc.custom_current_unit,
            })
            
            new_doc.copy_of_the_resume = 1 if doc.resume_attachment or doc.resume_link else 0
            new_doc.authorisation_letter = doc.custom_reference_check
            
            new_doc.insert(ignore_permissions=True)
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "new_job_condidate_application")

        
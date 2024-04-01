import frappe
import sys
import traceback


def create_personal_file_through_employee(doc,mothod=None):
    '''
    This function is use to create personal check list of old employee and new employee
    And also Update Personal Check List.
    
    Unique Key is aadhar_no and employee_id in personal check list and personal files.
    
    Step 1: first it is create personal check list.
    Step 2 : And than after it's Update Other details.
    '''
    try:
        create_personl_check_list_through_personal_file(doc)
        
        frappe.db.set_value("Personal file Check list",{"aadhar_no":doc.aadhar_no},{
            "current_ctc_structure": 1 if doc.current_ctc_structure else 0,
            "payslips_of_last_three_months":1 if doc.first_slip and doc.second_slip and doc.third_slip else 0,
            "reference_check_form_to_filled":1 if doc.reference_check_form_to_filled else 0,
            "image":1 if doc.image else 0,
            "educational_and_professional":1 if doc.educational_and_professional else 0,
            "employment_certificate": 1 if doc.employment_certificate else 0,
            "form_16_12ba":1 if doc.form_16_12ba else 0,
            "id_proof_and_address":1 if doc.id_proof_and_address else 0,
            "dob_proof":1 if doc.dob_proof else 0,
            "pan_card":1 if doc.pan_card else 0,
            "aadhar_card": 1 if doc.aadhar_card else 0,
            "vigil_mechanism_form":1 if doc.vigil_mechanism_form else 0,
            "cancel_cheque":1 if doc.cancel_cheque else 0,
            "locker_form":1 if doc.locker_form else 0,
            "issue_of_badge":1 if doc.issue_of_badge == "Yes" else 0,
            "uniform_issue_form":1 if doc.uniform_issue_form else 0,
            "nomination_mediclaim_form":1 if doc.nomination_mediclaim_form else 0,
            "nomination_form_from_2_revised":1 if doc.nomination_form_from_2_revised else 0,
            "esic_declaration":1 if doc.esic_declaration else 0,
            "form_gratuity":1 if doc.form_gratuity else 0,
            "medical_report":1 if doc.medical_report else 0,
            "copy_of_relieving_letter":1 if doc.copy_of_relieving_letter else 0,  
        })
        
        frappe.db.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "create_personal_file_through_employee")

    

def create_personl_check_list_through_personal_file(doc):
    try:
        if not frappe.db.exists("Personal file Check list",{"aadhar_no":doc.aadhar_no,"employee_id":doc.employee_id}):
                
                new_doc = frappe.get_doc({
                    "doctype":"Personal file Check list",
                    "employee_id":doc.employee_id,
                    "employee_name":doc.employee_name,
                    "aadhar_no":doc.aadhar_no,
                    "unit":doc.unit,
                })
                
                new_doc.insert(ignore_permissions=True)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "create_personl_check_list_through_personal_file")

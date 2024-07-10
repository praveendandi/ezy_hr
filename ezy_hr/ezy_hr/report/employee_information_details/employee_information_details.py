# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.utils import flt
# from frappe.utils import formatdate
# import json
# import sys
# import traceback

# def get_salary_components():
#     # Fetch all salary components
#     salary_components = frappe.get_all("Salary Component", fields=["name"])
#     return salary_components


# def execute(filters=None):
#     try:
#         columns = [
#             {"label": "Emp. No", "fieldname": "employee", "fieldtype": "Data"},
#             {"label": "First Name", "fieldname": "first_name", "fieldtype": "Data"},
#             {"label": "Middle Name", "fieldname": "middle_name", "fieldtype": "Data"},
#             {"label": "Last Name", "fieldname": "last_name", "fieldtype": "Data"},
#             {"label": "Gender", "fieldname": "gender", "fieldtype": "Data"},
#             {"label": "Date of Birth", "fieldname": "date_of_birth", "fieldtype": "Date"},
#             {"label": "Disability", "fieldname": "custom_disability", "fieldtype": "Select", "options": "Yes\nNo"},  
#             {"label": "Blood Group", "fieldname": "blood_group", "fieldtype": "Data"},
#             {"label": "Height", "fieldname": "custom_height", "fieldtype": "Data"},
#             {"label": "Weight", "fieldname": "custom_weight", "fieldtype": "Data"},
#             {"label": "Marital Status", "fieldname": "marital_status", "fieldtype": "Data"},
#             {"label": "Father Name", "fieldname": "custom_father_name", "fieldtype": "Data"},
#             {"label": "Mother Name", "fieldname": "custom_mother_name", "fieldtype": "Data"},
#             {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department"},
#             {"label": "Designation", "fieldname": "designation", "fieldtype": "Link", "options": "Designation"},
#             {"label": "Joining Date", "fieldname": "date_of_joining", "fieldtype": "Date"},
#             {"label": "Employment Type", "fieldname": "employment_type", "fieldtype": "Link","options": "Employment Type"},
#             {"label": "Official Mobile No", "fieldname": "custom_official_mobile_no", "fieldtype": "Data"},
#             {"label": "Personal Email", "fieldname": "personal_email", "fieldtype": "Data","options": "Email"},
#             {"label": "Emergency Contact Name", "fieldname": "person_to_be_contacted", "fieldtype": "Data",},
#             {"label": "Relationship", "fieldname": "relation", "fieldtype": "Data"},
#             {"label": "Aadhar No.", "fieldname": "custom_aadhar_no", "fieldtype": "Data"},
#             {"label": "Voter Id", "fieldname": "custom_voter_id_no", "fieldtype": "Data"},
#             {"label": "Permanent Address", "fieldname": "permanent_address", "fieldtype": "Small Text"},
#             {"label": "Permanent Address Line 1", "fieldname": "custom_permanent_address_line_1", "fieldtype": "Data"},
#             {"label": "Permanent Address Line 2", "fieldname": "custom_permanent_address_line_2", "fieldtype": "Data"},
#             {"label": "Permanent Address Line 3", "fieldname": "custom_permanent_address_line_3", "fieldtype": "Data"},
#             {"label": "Permanent City", "fieldname": "custom_permanent_city", "fieldtype": "Data"},
#             {"label": "Permanent State", "fieldname": "custom_permanent_state", "fieldtype": "Data"},
#             {"label": "Permanent Pin", "fieldname": "custom_permanent_pin", "fieldtype": "Data"},
#             {"label": "Current Address", "fieldname": "current_address", "fieldtype": "Small Text"},
#             {"label": "Current Address Line 1", "fieldname": "custom_address_line_1", "fieldtype": "Data"},
#             {"label": "Current Address Line 2", "fieldname": "custom_address_line_2", "fieldtype": "Data"},
#             {"label": "Current Address Line 3", "fieldname": "custom_address_line_3", "fieldtype": "Data"},
#             {"label": "City", "fieldname": "custom_city_", "fieldtype": "Data"},
#             {"label": "State", "fieldname": "custom_state", "fieldtype": "Data"},
#             {"label": "Pincode", "fieldname": "custom_pin_code", "fieldtype": "Data"},
#             {"label": "Name Of Nominee", "fieldname": "custom_name_of_nominee", "fieldtype": "Data"},
#             {"label": "Relationship With Nominee", "fieldname": "custom_relationship_with_nominee", "fieldtype": "Data"},
#             {"label": "Date Of Birth", "fieldname": "custom_nominee_date_of_birth", "fieldtype": "Date"},
#             {"label": "Nominee Address Line 1", "fieldname": "custom_nominee_address_line_1", "fieldtype": "Data"},
#             {"label": "Nominee District", "fieldname": "custom_nominee_district", "fieldtype": "Data"},
#             {"label": "Nominee Pin Code", "fieldname": "custom_nominee_pin_code", "fieldtype": "Data"},
#             {"label": "Custom Nominee Address Line 2", "fieldname": "custom_nominee_address_line_2", "fieldtype": "Data"},
#             {"label": "Nominee State", "fieldname": "custom_nominee_state", "fieldtype": "Data"},
#             {"label": "Bank Name", "fieldname":"bank_name","fieldtype":"Data"},
#             {"label": "Bank A/C No.", "fieldname":"bank_ac_no","fieldtype":"Data"},
#             {"label": "IFSC Code", "fieldname":"ifsc_code","fieldtype":"Data"},
#             {"label": "MICR Code", "fieldname":"micr_code","fieldtype":"Data"},
#             {"label": "IBAN", "fieldname":"iban","fieldtype":"Data"},
#             {"label": "Name Of Nominee 1", "fieldname": "custom_name_of_nominee_1", "fieldtype": "Data"},
#             {"label": "Relationship With Nominee 2", "fieldname": "custom_relationship_with_nominee_2", "fieldtype": "Data"},
#             {"label": "Date Of Birth 3", "fieldname": "custom_date_of_birth_3", "fieldtype": "Date"},
#             {"label": "Nominee Address Line 3", "fieldname": "custom_nominee_address_line_3", "fieldtype": "Data"},
#             {"label": "Custom Nominee District 1", "fieldname": "custom_nominee_district_1", "fieldtype": "Data"},
#             {"label": "Nominee Pin Code 1", "fieldname": "custom_nominee_pin_code_1", "fieldtype": "Data"},
#             {"label": "Nominee Address Line 4", "fieldname": "custom_nominee_address_line_4", "fieldtype": "Data"},
#             {"label": "Nominee State 2", "fieldname": "custom_nominee_state_2", "fieldtype": "Data"},
#         ]

#         # salary_components = get_salary_components()
#         # for component in salary_components:
#         #     columns.append({"label": component.name,
#         #                     "fieldname": component.name,
#         #                     "fieldtype": "Currency"})

#         data = []

#         condition = {}
#         if  filters.get("department"):
#             condition.update({"department": filters.get("department")})

#         if filters.get("company"):
#             condition.update({"company": filters.get("company")})
        
#         if filters.get("gender"):
#             condition.update({"gender": filters.get("gender")})
#         if filters.get("employee_type"):
#             condition.update({"employee_type": filters.get("employee_type")})
#         if filters.get("branch"):
#             condition.update({"branch": filters.get("branch")})
#         if filters.get("payroll_cost_center"):
#             condition.update({"payroll_cost_center": filters.get("payroll_cost_center")})

#         employees = frappe.get_all("Employee", filters=condition, fields=[
#             "name", "employee", "first_name", "middle_name", "last_name", "gender",
#             "date_of_birth", "custom_disability", "blood_group", "custom_height", "custom_weight", "marital_status",
#             "custom_father_name", "custom_mother_name", "department", "designation", "date_of_joining",
#             "employment_type", "status", 'custom_official_mobile_no','personal_email',"person_to_be_contacted","relation",
#             "custom_aadhar_no", "custom_voter_id_no","permanent_address","custom_permanent_address_line_1","custom_permanent_address_line_2",
#             "custom_permanent_address_line_3", "custom_permanent_city","custom_permanent_state", "custom_permanent_pin",'current_address',
#             "custom_address_line_1","custom_address_line_2","custom_address_line_3","custom_city_","custom_state", "custom_pin_code",
#             'custom_name_of_nominee','custom_relationship_with_nominee','custom_nominee_date_of_birth','custom_nominee_address_line_1','custom_nominee_district','custom_nominee_pin_code',
#             'custom_nominee_address_line_2','custom_nominee_state','bank_name','bank_ac_no',"ifsc_code","micr_code","iban",'custom_name_of_nominee_1','custom_relationship_with_nominee_2','custom_date_of_birth_3','custom_nominee_address_line_3',
#             'custom_nominee_district_1','custom_nominee_pin_code_1','custom_nominee_address_line_4','custom_nominee_state_2'
#         ])
        
#         for employee in employees:
#             department_name=None
#             if employee.department:
#                 department_name=employee.department.split(" - ")[0] if " - " in employee.department else  employee.department
#             row = {
#                 "employee": employee.employee,
#                 "first_name": employee.first_name,
#                 "middle_name": employee.middle_name,
#                 "last_name": employee.last_name,
#                 "gender": employee.gender,
                
#                 "date_of_birth":formatdate(employee.date_of_birth,"dd-mm-yyyy"),
#                 "custom_disability": employee.custom_disability,
#                 "blood_group": employee.blood_group,
#                 "custom_height": employee.custom_height,
#                 "custom_weight": employee.custom_weight,
#                 "marital_status": employee.marital_status,
#                 "custom_father_name": employee.custom_father_name,
#                 "custom_mother_name": employee.custom_mother_name,
#                 "department": department_name,
#                 "designation": employee.designation,
                
#                 "date_of_joining": formatdate(employee.date_of_joining,"dd-mm-yyyy"),
#                 "employment_type": employee.employment_type,
#                 "status": employee.status,
#                 'custom_official_mobile_no': employee.custom_official_mobile_no,
#                 'personal_email': employee.personal_email,
#                 'person_to_be_contacted': employee.person_to_be_contacted,
#                 "custom_aadhar_no": employee.custom_aadhar_no,
#                 "custom_voter_id_no": employee.custom_voter_id_no,
#                 "permanent_address": employee.permanent_address,
#                 "custom_permanent_address_line_1": employee.custom_permanent_address_line_1,
#                 "custom_permanent_address_line_2": employee.custom_permanent_address_line_2,
#                 "custom_permanent_address_line_3": employee.custom_permanent_address_line_3,
#                 "custom_permanent_city": employee.custom_permanent_city,
#                 "custom_permanent_state": employee.custom_permanent_state,
#                 "current_address": employee.current_address,
#                 "custom_address_line_1": employee.custom_address_line_1,
#                 "custom_address_line_2": employee.custom_address_line_2,
#                 "custom_address_line_3": employee.custom_address_line_3,
#                 "custom_city_": employee.custom_city_,
#                 "custom_state": employee.custom_state,
#                 "custom_pin_code": employee.custom_pin_code,
#                 'custom_name_of_nominee': employee.custom_name_of_nominee,
#                 'custom_relationship_with_nominee': employee.custom_relationship_with_nominee,
#                 'custom_nominee_date_of_birth': employee.custom_nominee_date_of_birth,
#                 'custom_nominee_address_line_1': employee.custom_nominee_address_line_1,
#                 'custom_nominee_district': employee.custom_nominee_district,
#                 'custom_nominee_pin_code': employee.custom_nominee_pin_code,
#                 'custom_nominee_address_line_2': employee.custom_nominee_address_line_2,
#                 'custom_nominee_state': employee.custom_nominee_state,
#                 'bank_name':employee.bank_name,
#                 'bank_ac_no':employee.bank_ac_no,
#                 "ifsc_code":employee.ifsc_code,
#                 "micr_code":employee.micr_code,
#                 "iban":employee.iban,
#                 'custom_name_of_nominee_1': employee.custom_name_of_nominee_1,
#                 'custom_relationship_with_nominee_2': employee.custom_relationship_with_nominee_2,
#                 'custom_date_of_birth_3': employee.custom_date_of_birth_3,
#                 'custom_nominee_address_line_3': employee.custom_nominee_address_line_3,
#                 'custom_nominee_district_1': employee.custom_nominee_district_1,
#                 'custom_nominee_pin_code_1': employee.custom_nominee_pin_code_1,
#                 'custom_nominee_address_line_4': employee.custom_nominee_address_line_4,
#                 'custom_nominee_state_2': employee.custom_nominee_state_2,
#             }
#             assignments = frappe.get_all("Salary Structure Assignment",
#                                             filters={"employee": employee.name},
#                                             fields=["name", "salary_structure"])
#             for assignment in assignments:
#                 salary_structure = frappe.get_doc("Salary Structure", assignment.salary_structure)
#                 for component in salary_structure.get("earnings"):
#                     row[component.salary_component] = component.amount
#                 for component in salary_structure.get("deductions"):
#                     row[component.salary_component] = component.amount

#             data.append(row)

#         return columns, data
    
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "execute")


import frappe
from frappe import _
from frappe.utils import flt
import json
import sys
import traceback
from datetime import datetime


def execute(filters=None):
   
   columns = get_columns(filters)
   data = get_data(filters)
   
   return columns, data



def get_data(filters):
   data = []

   condition = {}
   if  filters.get("status"):
       condition.update({"status": filters.get("status")})
       
   if  filters.get("department"):
       condition.update({"department": filters.get("department")})

   if filters.get("company"):
       condition.update({"company": filters.get("company")})
   
   if filters.get("gender"):
       condition.update({"gender": filters.get("gender")})
   if filters.get("employee_type"):
       condition.update({"employee_type": filters.get("employee_type")})
   if filters.get("branch"):
       condition.update({"branch": filters.get("branch")})
   if filters.get("payroll_cost_center"):
       condition.update({"payroll_cost_center": filters.get("payroll_cost_center")})

   employees = frappe.db.get_list("Employee", filters=condition, fields=[
       "name", "employee", "first_name", "middle_name", "last_name", "gender",
       "date_of_birth", "custom_disability", "blood_group", "custom_height", "custom_weight", "marital_status",
       "custom_father_name", "custom_mother_name", "department", "designation", "date_of_joining",
       "employment_type", "status", 'custom_official_mobile_no','personal_email',"person_to_be_contacted","relation",
       "custom_aadhar_no", "custom_voter_id_no","permanent_address","custom_permanent_address_line_1","custom_permanent_address_line_2",
       "custom_permanent_address_line_3", "custom_permanent_city","custom_permanent_state", "custom_permanent_pin",'current_address',
       "custom_address_line_1","custom_address_line_2","custom_address_line_3","custom_city_","custom_state", "custom_pin_code",
       'custom_name_of_nominee','custom_relationship_with_nominee','custom_nominee_date_of_birth','custom_nominee_address_line_1','custom_nominee_district','custom_nominee_pin_code',
       'custom_nominee_address_line_2','custom_nominee_state','bank_name','bank_ac_no',"ifsc_code","micr_code","iban",'custom_name_of_nominee_1','custom_relationship_with_nominee_2','custom_date_of_birth_3','custom_nominee_address_line_3',
       'custom_nominee_district_1','custom_nominee_pin_code_1','custom_nominee_address_line_4','custom_nominee_state_2'
   ])
   
   for employee in employees:
       department_name=None
       if employee.department:
           department_name=employee.department.split(" - ")[0] if " - " in employee.department else  employee.department
       
       date_of_birth = employee.get("date_of_birth").strftime("%d-%m-%Y")
       date_of_joining = employee.get("date_of_joining").strftime("%d-%m-%Y")
       
       row = {
           "employee": employee.employee,
           "first_name": employee.first_name,
           "middle_name": employee.middle_name,
           "last_name": employee.last_name,
           "gender": employee.gender,
           "date_of_birth":date_of_birth,
           "custom_disability": employee.custom_disability,
           "blood_group": employee.blood_group,
           "custom_height": employee.custom_height,
           "custom_weight": employee.custom_weight,
           "marital_status": employee.marital_status,
           "custom_father_name": employee.custom_father_name,
           "custom_mother_name": employee.custom_mother_name,
           "department": department_name,
           "designation": employee.designation,
           "date_of_joining": date_of_joining,
           "employment_type": employee.employment_type,
           "status": employee.status,
           'custom_official_mobile_no': employee.custom_official_mobile_no,
           'personal_email': employee.personal_email,
           'person_to_be_contacted': employee.person_to_be_contacted,
           "custom_aadhar_no": employee.custom_aadhar_no,
           "custom_voter_id_no": employee.custom_voter_id_no,
           "permanent_address": employee.permanent_address,
           "custom_permanent_address_line_1": employee.custom_permanent_address_line_1,
           "custom_permanent_address_line_2": employee.custom_permanent_address_line_2,
           "custom_permanent_address_line_3": employee.custom_permanent_address_line_3,
           "custom_permanent_city": employee.custom_permanent_city,
           "custom_permanent_state": employee.custom_permanent_state,
           "current_address": employee.current_address,
           "custom_address_line_1": employee.custom_address_line_1,
           "custom_address_line_2": employee.custom_address_line_2,
           "custom_address_line_3": employee.custom_address_line_3,
           "custom_city_": employee.custom_city_,
           "custom_state": employee.custom_state,
           "custom_pin_code": employee.custom_pin_code,
           'custom_name_of_nominee': employee.custom_name_of_nominee,
           'custom_relationship_with_nominee': employee.custom_relationship_with_nominee,
           'custom_nominee_date_of_birth': employee.custom_nominee_date_of_birth,
           'custom_nominee_address_line_1': employee.custom_nominee_address_line_1,
           'custom_nominee_district': employee.custom_nominee_district,
           'custom_nominee_pin_code': employee.custom_nominee_pin_code,
           'custom_nominee_address_line_2': employee.custom_nominee_address_line_2,
           'custom_nominee_state': employee.custom_nominee_state,
           'bank_name':employee.bank_name,
           'bank_ac_no':employee.bank_ac_no,
           "ifsc_code":employee.ifsc_code,
           "micr_code":employee.micr_code,
           "iban":employee.iban,
           'custom_name_of_nominee_1': employee.custom_name_of_nominee_1,
           'custom_relationship_with_nominee_2': employee.custom_relationship_with_nominee_2,
           'custom_date_of_birth_3': employee.custom_date_of_birth_3,
           'custom_nominee_address_line_3': employee.custom_nominee_address_line_3,
           'custom_nominee_district_1': employee.custom_nominee_district_1,
           'custom_nominee_pin_code_1': employee.custom_nominee_pin_code_1,
           'custom_nominee_address_line_4': employee.custom_nominee_address_line_4,
           'custom_nominee_state_2': employee.custom_nominee_state_2,
       }
       # assignments = frappe.get_all("Salary Structure Assignment",
       #                                 filters={"employee": employee.name},
       #                                 fields=["name", "salary_structure"])
       # for assignment in assignments:
       #     salary_structure = frappe.get_doc("Salary Structure", assignment.salary_structure)
       #     for component in salary_structure.get("earnings"):
       #         row[component.salary_component] = component.amount
       #     for component in salary_structure.get("deductions"):
       #         row[component.salary_component] = component.amount

       data.append(row)
 
   return data




def get_columns(filters):
   columns = [
       {
           "label": (_("Emp. No")),
           "fieldname": "employee",
           "fieldtype": "Link",
           "options":"Employee",
         },
       # {
       #   "label": (_("Emp. No")),
       #   "fieldname": "employee", 
       #   "fieldtype": "Data"
       # },
       {
           "label": (_("First Name")),
           "fieldname": "first_name",
           "fieldtype": "Data",
       },
       {
             "label": (_("Middle Name")),
           "fieldname": "middle_name",
            "fieldtype": "Data",
       },
       {
           "label": (_("Last Name")),
           "fieldname": "last_name", 
           "fieldtype": "Data",
       },
       {
           "label": (_("Gender")),
           "fieldname": "gender", 
           "fieldtype": "Data",
       },
       {
           "label":(_("Date of Birth")),
           "fieldname": "date_of_birth", 
           "fieldtype": "Data",
       },
       {
           "label": (_("Status")),
           "fieldname": "status",
           "fieldtype": "Data",
       },
       {
           "label":(_("Disability")),
           "fieldname": "custom_disability", 
           "fieldtype": "Select",
           "options": "Yes\nNo",
       },  
       {
           "label": (_("Blood Group")),
           "fieldname": "blood_group", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Height")), 
           "fieldname":"custom_height",
           "fieldtype": "Data"
       },
       {
           "label": (_("Weight")),
           "fieldname": "custom_weight", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Marital Status")), 
           "fieldname": "marital_status", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Father Name")),
           "fieldname": "custom_father_name", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Mother Name")), 
           "fieldname": "custom_mother_name", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Department")), 
           "fieldname": "department", 
           "fieldtype": "Link", 
           "options": "Department"
       },
       {
           "label": (_("Designation")), 
           "fieldname": "designation", 
           "fieldtype": "Link", 
           "options": "Designation"
       },
       {
           "label": (_("Joining Date")), 
           "fieldname": "date_of_joining", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Employment Type")), 
           "fieldname": "employment_type", 
           "fieldtype": "Link","options": 
           "Employment Type"
       },
       {
           "label": (_("Official Mobile No")), 
           "fieldname": "custom_official_mobile_no", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Personal Email")), 
           "fieldname": "personal_email", 
           "fieldtype": "Data",
           "options": "Email"
       },
       {
           "label": (_("Emergency Contact Name")), 
           "fieldname": "person_to_be_contacted", 
           "fieldtype": "Data",
       },
       {
           "label": (_("Relationship")), 
           "fieldname": "relation", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Aadhar No.")), 
           "fieldname": "custom_aadhar_no", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Voter Id")), 
           "fieldname": "custom_voter_id_no", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Permanent Address")), 
           "fieldname": "permanent_address", 
           "fieldtype": "Small Text"
       },
       {
           "label": (_("Permanent Address Line 1")), 
           "fieldname": "custom_permanent_address_line_1", 
           "fieldtype": "Data"
       },
       {
             "label": (_("Permanent Address Line 2")), 
           "fieldname": "custom_permanent_address_line_2", 
            "fieldtype": "Data"
       },
       {
           "label": (_("Permanent Address Line 3")), 
           "fieldname": "custom_permanent_address_line_3",
           "fieldtype": "Data"
       },
       {
           "label": (_("Permanent City")),
           "fieldname": "custom_permanent_city", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Permanent State")), 
           "fieldname": "custom_permanent_state", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Permanent Pin")),
           "fieldname": "custom_permanent_pin", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Current Address")), 
           "fieldname": "current_address", 
           "fieldtype": "Small Text"
       },
       {
           "label": (_("Current Address Line 1")),
           "fieldname": "custom_address_line_1", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Current Address Line 2")), 
           "fieldname": "custom_address_line_2", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Current Address Line 3")), 
           "fieldname": "custom_address_line_3", 
           "fieldtype": "Data"
       },
       {
           "label": (_("City")), 
           "fieldname": "custom_city_", 
           "fieldtype": "Data"
       },
       {
           "label": (_("State")), 
           "fieldname": "custom_state", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Pincode")),
           "fieldname": "custom_pin_code",
           "fieldtype": "Data"
       },
       {
           "label": (_("Name Of Nominee")),
           "fieldname": "custom_name_of_nominee", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Relationship With Nominee")), 
           "fieldname": "custom_relationship_with_nominee",
           "fieldtype": "Data"
       },
       {   
           "label": (_("Date Of Birth")), 
           "fieldname": "custom_nominee_date_of_birth",
           "fieldtype": "Date"
       },
       {
           "label": (_("Nominee Address Line 1")), 
           "fieldname": "custom_nominee_address_line_1", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee District")), 
           "fieldname": "custom_nominee_district", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee Pin Code")),
           "fieldname": "custom_nominee_pin_code", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Custom Nominee Address Line 2")), 
           "fieldname": "custom_nominee_address_line_2", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee State")), 
           "fieldname": "custom_nominee_state", 
           "fieldtype": "Data"
       },
       {
           "label":  (_("Bank Name")), 
           "fieldname":"bank_name",
           "fieldtype":"Data"
       },
       {
           "label": (_("Bank A/C No.")),
           "fieldname":"bank_ac_no",
           "fieldtype":"Data"
       },
       {
           "label": (_("IFSC Code")), 
           "fieldname":"ifsc_code",
           "fieldtype":"Data"
       },
       {
           "label": (_("MICR Code")), 
           "fieldname":"micr_code",
           "fieldtype":"Data"
       },
       {
           "label": (_("IBAN")), 
           "fieldname":"iban",
           "fieldtype":"Data"
       },
       {
           "label": (_("Name Of Nominee 1")), 
           "fieldname": "custom_name_of_nominee_1", 
           "fieldtype": "Data"
       },
       {
             "label": (_("Relationship With Nominee 2")),
           "fieldname": "custom_relationship_with_nominee_2", 
            "fieldtype": "Data"
       },
       {
           "label": (_("Date Of Birth 3")),
           "fieldname": "custom_date_of_birth_3",
           "fieldtype": "Date"
       },
       {
           "label": (_("Nominee Address Line 3")), 
           "fieldname": "custom_nominee_address_line_3", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Custom Nominee District 1")), 
           "fieldname": "custom_nominee_district_1", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee Pin Code 1")), 
           "fieldname": "custom_nominee_pin_code_1", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee Address Line 4")), 
           "fieldname": "custom_nominee_address_line_4", 
           "fieldtype": "Data"
       },
       {
           "label": (_("Nominee State 2")),
           "fieldname": "custom_nominee_state_2", 
           "fieldtype": "Data"
       },
 ]
   
   return columns
   
   





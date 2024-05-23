# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
import sys
import traceback

def execute(filters=None):
    try:
        columns, data = [], []
  
        columns = get_columns()
        data = get_data(filters)
        return columns, data

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "execute")

     

def get_columns():
    return [
        {"fieldname": "company", "label": "Unit", "fieldtype": "Data", "width": 150},
        {"fieldname": "male", "label": "Male", "fieldtype": "Int", "width": 100},
        {"fieldname": "female", "label": "Female", "fieldtype": "Int", "width": 100},
        {"fieldname": "labour_welfare_employee", "label": "Employee", "fieldtype": "Currency", "width": 150},
        {"fieldname": "labour_welfare_employer", "label": "Employer", "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_lwf_payable", "label": "Total LWF Payable", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
    data = []
    
    company_filter = {}
    if filters and filters.get("company"):
        company_filter = {"name": filters.get("company")}
    
    companies = frappe.get_all("Company", filters=company_filter, fields=["name"])
    
    for company in companies:
        male = 0
        female = 0
        
        labour_welfare_employee = 0
        labour_welfare_employer = 0
        
        salary_slip_filter = {}
        
        salary_slip_filter.update({
            "company":company.name,
            "start_date":filters.get("from_date"),
            "end_date":filters.get("end_date")
        })
        
        salary_slips = frappe.get_all("Salary Slip", filters = salary_slip_filter, fields=["name", "employee"])
        
        for slip in salary_slips:
            child_entries = frappe.get_all("Salary Detail", filters={"parent": slip.name, "salary_component": ["in", ["Labour Welfare Employee", "Labour Welfare Employer"]]}, fields=["salary_component", "amount"])
            
            if not child_entries:
                continue  
            
            employee_gender = frappe.db.get_value("Employee", slip.employee, "gender")
            if employee_gender == "Male":
                male += 1
            elif employee_gender == "Female":
                female += 1
            
            for entry in child_entries:
                if entry.salary_component == "Labour Welfare Employee":
                    labour_welfare_employee += entry.amount or 0
                elif entry.salary_component == "Labour Welfare Employer":
                    labour_welfare_employer += entry.amount or 0
        
        total_lwf_payable = labour_welfare_employee + labour_welfare_employer

        row = {
            "company": company.name,
            "male": male,
            "female": female,
            "labour_welfare_employee": labour_welfare_employee,
            "labour_welfare_employer": labour_welfare_employer,
            "total_lwf_payable": total_lwf_payable,
        }
        data.append(row)
    
    return data

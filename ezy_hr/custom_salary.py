import frappe
import erpnext
import sys
import traceback
from datetime import datetime


def create_salary_structure_through_employee(doc,mothod=None):
    try:
        row_data = doc.as_dict()
        earnings = []
        deductions = []
        
        current_month = None
        current_year = None
        
        if doc.custom_effective_date:
            change_str = doc.custom_effective_date
            # change_date = datetime.strptime(change_str, '%Y-%m-%d')
            current_year = change_str.year
            current_month = change_str.month
            
        if doc.custom_effective_date:
            if not frappe.db.exists("Salary Structure",{"name":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})","is_active":"Yes","docstatus":1}):
                if len(row_data.get("custom_earnings",[])) >0:
                    for each_earn in row_data.get("custom_earnings"):
                        earning = {
                            "doctype":"Salary Detail",
                            "parent": f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",
                            "parentfield" :"earnings",
                            "parenttype":"Salary Structure",
                            "salary_component":each_earn.get("salary_component"),
                            "abbr":each_earn.get("abbr"),
                            "amount":each_earn.get("amount"),
                        }
                        earnings.append(earning)
                        
                    for each_deduc in row_data.get("custom_deductions"):
                        deduction = {
                            "doctype":"Salary Detail",
                            "parent":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",
                            "parentfield" :"deductions",
                            "parenttype":"Salary Structure",
                            "salary_component":each_deduc.get("salary_component"),
                            "abbr":each_deduc.get("abbr"), 
                        }
                        
                        if each_deduc.get("amount_based_on_formula") and each_deduc.get("formula"):
                            deduction.update({
                                "condition":each_deduc.get("custom_employee_condition"),
                                "amount_based_on_formula":1,
                                "formula":each_deduc.get("formula"),
                                "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
                            })
                        else:
                            if each_deduc.get("custom_employee_condition"):
                                deduction.update({
                                    "condition":each_deduc.get("custom_employee_condition"),
                                    "amount":each_deduc.get("amount"),
                                    "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
                                })
                            else:
                                deduction.update({
                                    "amount":each_deduc.get("amount")
                                })
                        
                        deductions.append(deduction)
                        
                    details = {
                        "doctype": "Salary Structure",
                        "name": f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",
                        "company": doc.company or erpnext.get_default_company(),
                        "earnings": earnings,
                        "deductions":deductions,
                        "payroll_frequency": "Monthly",
                        "currency": "INR",
                        "is_active":"Yes",
                        "docstatus":1
                    }
                    
                    salary_structure_doc = frappe.get_doc(details)
                    salary_structure_doc.insert()
                    
                    if salary_structure_doc.name and salary_structure_doc.docstatus == 1:
                        salary_structure_assignment(doc,salary_structure_doc.name)
                
            else:
                update_salary_structure(doc,current_year,current_month)
                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "create_salary_structure_through_employee")

def salary_structure_assignment(doc,salary_structure):
    
    def get_income_tax_slab():
        
        income_tax_slab = frappe.db.get_value(
            'Income Tax Slab',
            filters={"name":("like",("%Old Tax%")),"disabled":0,"company":doc.company or erpnext.get_default_company()},
            fieldname=['name']
        )
        
        return income_tax_slab

    
    assignment_details = {
        "doctype": "Salary Structure Assignment",
        "employee":doc.name,
        "salary_structure":salary_structure,
        "from_date":frappe.get_value("Employee",{"name":doc.name},['date_of_joining']) if not doc.custom_effective_date else doc.custom_effective_date,
        "income_tax_slab":doc.custom_income_tax_slab if doc.custom_income_tax_slab else get_income_tax_slab() ,
        "docstatus":1,
        "base":doc.custom_gross_amount
    }
    salary_structure_assig = frappe.get_doc(assignment_details)
    salary_structure_assig.insert()
    
    
 
def update_salary_structure(doc,current_year,current_month):
    
    custom_earnings_updates(doc,current_year,current_month)
    custom_deductions_updates(doc,current_year,current_month)
    
        
def custom_earnings_updates(doc,current_year,current_month):
   
    try:  
        new_row_data = doc.as_dict()
        if len(new_row_data.get("custom_earnings",[])) >0:
            new_component_counts = len(new_row_data.get("custom_earnings", []))
            
            new_component_amount = sum(each.get("amount", 0) for each in new_row_data.get("custom_earnings", []))
            
            previous_component_counts = frappe.db.sql(
                """
                SELECT COUNT(sd.idx) as count
                FROM 
                `tabSalary Detail` as sd,
                `tabSalary Structure` as ss
                WHERE 
                sd.parent = ss.name
                And sd.parentfield = "earnings"
                And ss.docstatus=1 
                And ss.name = (%s)
                And ss.company =(%s)
                """,(f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",doc.company),
                as_list=1
            )[0][0]

            previous_component_amount = frappe.db.sql(
                """
                SELECT SUM(sd.amount) as amount
                FROM 
                `tabSalary Detail` as sd,
                `tabSalary Structure` as ss
                WHERE 
                sd.parent = ss.name
                And sd.parentfield = "earnings"
                And ss.docstatus=1 
                And ss.name = (%s)
                And ss.company =(%s)
                """,(f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",doc.company),
                as_list=1
            )[0][0]

            if new_component_counts != previous_component_counts or new_component_amount != previous_component_amount:
                
                for each in frappe.get_all("Salary Detail",filters={"parent":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})","parentfield":"earnings","docstatus":1,"parenttype":"Salary Structure"}):
                    
                    frappe.db.delete("Salary Detail",{"name":each.name,"parentfield":"earnings","docstatus":1,"parenttype":"Salary Structure"})
                    
                    frappe.clear_cache(doctype="Salary Detail")
                
                    frappe.db.commit()
                    
                new_child_records = []
                for each_earn in new_row_data.get("custom_earnings"):
                    earning = {
                        "doctype": "Salary Detail",
                        "parent": f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",
                        "parentfield": "earnings",
                        "parenttype": "Salary Structure",
                        "salary_component": each_earn.get("salary_component"),
                        "abbr": each_earn.get("abbr"),
                        "amount": each_earn.get("amount"),
                    }
                    new_child_records.append(earning)
                    
                document = frappe.get_doc("Salary Structure",f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})")
                
                for record in new_child_records:
                    child_doc = frappe.new_doc('Salary Detail')
                    child_doc.update(record)
                    document.append('earnings', child_doc)
                    
                document.save()
                                
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "custom_earnings_updates")

           
def custom_deductions_updates(doc,current_year,current_month):
    
    try:
        new_row_data = doc.as_dict()
        
        if len(new_row_data.get("custom_deductions",[])) >0: 
            new_component_counts = len(new_row_data.get("custom_deductions", []))
            
            new_component_amount = sum(each.get("amount", 0) for each in new_row_data.get("custom_deductions", []))
            
            previous_component_counts = frappe.db.sql(
                """
                SELECT COUNT(sd.idx) as count
                FROM 
                `tabSalary Detail` as sd,
                `tabSalary Structure` as ss
                WHERE 
                sd.parent = ss.name
                And sd.parentfield = "deductions"
                And ss.docstatus=1 
                And ss.name = (%s)
                And ss.company =(%s)
                """,(f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",doc.company),
                as_list=1
            )[0][0]

            previous_component_amount = frappe.db.sql(
                """
                SELECT SUM(sd.amount) as amount
                FROM 
                `tabSalary Detail` as sd,
                `tabSalary Structure` as ss
                WHERE 
                sd.parent = ss.name
                And sd.parentfield = "deductions"
                And ss.docstatus=1 
                And ss.name = (%s)
                And ss.company =(%s)
                """,(f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",doc.company),
                as_list=1
            )[0][0]

            if new_component_counts != previous_component_counts or new_component_amount != previous_component_amount:
                
                for each in frappe.get_all("Salary Detail",filters={"parent":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})","parentfield":"deductions","docstatus":1,"parenttype":"Salary Structure"}):
                    
                    frappe.db.delete("Salary Detail",{"name":each.name,"parentfield":"deductions","docstatus":1,"parenttype":"Salary Structure"})
                    
                    frappe.clear_cache(doctype="Salary Detail")
                
                    frappe.db.commit()
                    
                new_child_records = []
                for each_deduc in new_row_data.get("custom_deductions"):
                    deduction = {
                        "doctype":"Salary Detail",
                        "parent":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})",
                        "parentfield" :"deductions",
                        "parenttype":"Salary Structure",
                        "salary_component":each_deduc.get("salary_component"),
                        "abbr":each_deduc.get("abbr"), 
                    }
                    
                    if each_deduc.get("amount_based_on_formula") and each_deduc.get("formula"):
                            deduction.update({
                                "condition":each_deduc.get("custom_employee_condition"),
                                "amount_based_on_formula":1,
                                "formula":each_deduc.get("formula"),
                                "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
                            })
                    else:
                        if each_deduc.get("custom_employee_condition"):
                            deduction.update({
                                "condition":each_deduc.get("custom_employee_condition"),
                                "amount":each_deduc.get("amount"),
                                "do_not_include_in_total": 1 if each_deduc.get("do_not_include_in_total") else 0
                            })
                        else:
                            deduction.update({
                                "amount":each_deduc.get("amount")
                            })
                        
                    new_child_records.append(deduction)
                    
                document = frappe.get_doc("Salary Structure",f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})")
                
                for record in new_child_records:
                    child_doc = frappe.new_doc('Salary Detail')
                    child_doc.update(record)
                    document.append('deductions', child_doc)
                    
                document.save()
        else:
            is_change = False
            for each in frappe.get_all("Salary Detail",filters={"parent":f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})","parentfield":"deductions","docstatus":1,"parenttype":"Salary Structure"}):
                    
                frappe.db.delete("Salary Detail",{"name":each.name,"parentfield":"deductions","docstatus":1,"parenttype":"Salary Structure"})
                
                frappe.clear_cache(doctype="Salary Detail")
            
                frappe.db.commit()
                is_change = True
             
            if is_change:       
                document = frappe.get_doc("Salary Structure",f"{doc.name}-{doc.employee_name}-({current_month}-{current_year})")
                document.save()
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "custom_deductions_updates")



def update_gross_amount(doc,method=None):
    try:
        new_row_data = doc.as_dict()
        if len(new_row_data.get("custom_earnings",[])) >0:
            new_component_amount = sum(each.get("amount", 0) for each in new_row_data.get("custom_earnings", []))
            frappe.client.set_value("Employee",{"name":new_row_data.get("name")},{"custom_gross_amount":new_component_amount})
            frappe.db.committ()
            
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "update_gross_amount")

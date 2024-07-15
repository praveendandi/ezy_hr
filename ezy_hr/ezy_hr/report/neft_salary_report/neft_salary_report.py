# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from collections import defaultdict

def execute(filters=None):
    if filters and filters.get("summarized_view"):
        columns = get_summarized_columns()
        data = get_summarized_data(filters)
    else:
        columns = get_columns()
        data = get_data(filters)
        
        if filters and filters.get("employment_type"):
            if filters["employment_type"] == "Employee":
                data = [entry for entry in data if not (entry.get("employee") and "-T" in entry["employee"])]
            else:
                data = [entry for entry in data if entry.get("employee") and "-T" in entry["employee"]]
    
    return columns, data

def get_columns():
    columns = [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 100},
        {"label": "Txn Type", "fieldname": "txn_type", "fieldtype": "Data", "width": 150},
        {"label": "Credit Account Number", "fieldname": "bank_account_no", "fieldtype": "Data", "width": 150},
        {"label": "Credit Account Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},        
        {"label": "IFSC", "fieldname": "custom_ifsc", "fieldtype": "Data", "width": 150},
        {"label": "Bank Name", "fieldname": "bank_name", "fieldtype": "Data", "width": 150},
        {"label": "Amount", "fieldname": "net_pay", "fieldtype": "Currency", "width": 150},
        {"label": "Narration", "fieldname": "narration", "fieldtype": "Data", "width": 150},
        {"label": "Attendance Device Id", "fieldname": "attendance_device_id", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Data", "width": 150},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150}
    ]
    return columns

def get_data(filters):
    final_data = []
    condition = {}
    if filters.from_date and filters.to_date:
        condition.update({"start_date": ["between", [filters.from_date, filters.to_date]]})
    if filters.company:
        condition.update({"company": filters.company})
    if filters.employee:
        condition.update({"employee": filters.employee})

    if filters.select_bank:
        if filters.select_bank == "YES BANK":
            condition.update({"bank_name": "YES BANK"})
            condition.update({"docstatus": 1})
        elif filters.select_bank == "Hold":
            condition.update({"docstatus": 0})
        else:
            condition.update({"bank_name": ["!=", "YES BANK"]})
            condition.update({"docstatus": 1})
    
    emp_salary = frappe.db.get_list("Salary Slip", filters=condition, fields=[
        'employee', 'company', 'employee_name', 'net_pay', 'bank_name', 'bank_account_no',
        'custom_ifsc', 'department', 'designation', 'status'
    ])
    
    emp_attendance_id = frappe.db.get_list("Employee", fields=['name', 'attendance_device_id'])
    emp_attendance_map = {emp['name']: emp['attendance_device_id'] for emp in emp_attendance_id}

    for i in emp_salary:
        if i['status'] == 'Draft':
            i['bank_name'] = 'Hold'
            i['net_pay'] = 0

        month = filters.get("from_date")
        date_obj = datetime.strptime(month, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B-%Y")
        narration = f'Salary {formatted_date}'
        i.update({"narration": narration})
        i.update({"txn_type": "NEFT"})
        i.update({"attendance_device_id": emp_attendance_map.get(i['employee'])})
        final_data.append(i)

    return final_data

def get_summarized_columns():
    columns = [
        {"label": "Unit", "fieldname": "company", "fieldtype": "Data", "width": 220},
        {"label": "Bank Name", "fieldname": "processed_through", "fieldtype": "Data", "width": 180},
        {"label": "Head Count", "fieldname": "head_count", "fieldtype": "Data", "width": 150},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 150}
    ]
    return columns

def get_summarized_data(filters):
    source_data = fetch_source_data(filters)
    combined_data = defaultdict(lambda: {"employee_count": 0, "amount": 0.0, "companies": set()})

    for entry in source_data:
        if filters and filters.get("employment_type"):
            if (filters["employment_type"] == "Employee" and "-T" in entry["employee"]) or \
               (filters["employment_type"] == "Intern" and "-T" not in entry["employee"]):
                continue

        if filters.select_bank:
            if filters.select_bank == "YES BANK" and entry.get("bank_name") != "YES BANK":
                continue
            elif filters.select_bank == "Hold" and entry.get("bank_name") != "Hold":
                continue
            elif filters.select_bank not in ["YES BANK", "Hold"] and entry.get("bank_name") in ["YES BANK", "Hold"]:
                continue
                
        bank_name = entry.get("bank_name") or " "
        company = entry.get("company")
        amount = entry.get("net_pay", 0.0)

        combined_data[bank_name]["employee_count"] += 1
        combined_data[bank_name]["amount"] += amount
        combined_data[bank_name]["companies"].add(company)
    
    data = []
    for bank_name, aggregate in combined_data.items():
        data.append({
            "company": ", ".join(aggregate["companies"]),
            "processed_through": bank_name,
            "head_count": aggregate["employee_count"], 
            "amount": aggregate["amount"]
        })
    
    return data

def fetch_source_data(filters):
    submitted_condition = {"docstatus": 1}
    draft_condition = {"docstatus": 0}

    if filters.get("from_date") and filters.get("to_date"):
        submitted_condition.update({"start_date": ["between", [filters["from_date"], filters["to_date"]]]})
        draft_condition.update({"start_date": ["between", [filters["from_date"], filters["to_date"]]]})
    if filters.get("company"):
        submitted_condition.update({"company": filters["company"]})
        draft_condition.update({"company": filters["company"]})
    if filters.get("employee"):
        submitted_condition.update({"employee": filters["employee"]})
        draft_condition.update({"employee": filters["employee"]})
    if filters.get("select_bank"):
        if filters["select_bank"] == "YES BANK":
            submitted_condition.update({"bank_name": "YES BANK"})
        elif filters["select_bank"] == "Hold":
            draft_condition.update({"docstatus": 0})
        else:
            submitted_condition.update({"bank_name": ["!=", "YES BANK"]})
    
    submitted_salary_slips = frappe.db.get_list("Salary Slip", filters=submitted_condition, fields=[
        'employee', 'company', 'employee_name', 'net_pay', 'bank_name', 'bank_account_no',
        'custom_ifsc', 'department', 'designation'
    ])

    draft_salary_slips = frappe.db.get_list("Salary Slip", filters=draft_condition, fields=[
        'employee', 'company', 'employee_name', 'net_pay', 'bank_name', 'bank_account_no',
        'custom_ifsc', 'department', 'designation'
    ])
    for slip in draft_salary_slips:
        slip['bank_name'] = 'Hold'
        slip['net_pay'] = 0.0

    emp_salary = submitted_salary_slips + draft_salary_slips

    return emp_salary





# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt

# import frappe


import frappe
from frappe.utils import getdate, add_months, formatdate
from datetime import timedelta


def execute(filters=None):
    if filters is None:
        filters = {}
    
    # Ensure default report_type is applied if not selected
    report_type = filters.get("report_type", "Summary Report")
    
    # Validate report_type and default to "Summary Report" if invalid
    if report_type not in ["Head Count Working", "New Joinees List", "Left Employees", "Summary Report"]:
        report_type = "Summary Report"  # Default to Summary Report if an invalid type is provided
    
    # Update filters with the corrected report_type
    filters["report_type"] = report_type
    
    columns = get_columns(report_type)
    data = get_data(filters, report_type)
    
    return columns, data

def get_columns(report_type):
    if report_type == "Head Count Working":
        return [
            {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 120},
            {"fieldname": "staff_count", "label": "Staff Count", "fieldtype": "Int", "width": 100}
        ]
    elif report_type == "New Joinees List":
        return [
            {"fieldname": "employee", "label": "Employee", "fieldtype": "Data", "width": 150},
            {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 150},
            {"fieldname": "date_of_joining", "label": "Date of Joining", "fieldtype": "Date", "width": 100},
            {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 120},
            {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
            {"fieldname": "gender", "label": "Gender", "fieldtype": "Data", "width": 100},
            {"fieldname": "date_of_birth", "label": "Date of Birth", "fieldtype": "Date", "width": 100},
            {"fieldname": "company", "label": "Unit", "fieldtype": "Data", "width": 150}
        ]
    elif report_type == "Left Employees":
        return [
            {"fieldname": "employee_name", "label": "Employee Name", "fieldtype": "Data", "width": 150},
            {"fieldname": "employee", "label": "Employee", "fieldtype": "Data", "width": 150},
            {"fieldname": "relieving_date", "label": "Relieving Date", "fieldtype": "Date", "width": 100},
            {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 120},
            {"fieldname": "designation", "label": "Designation", "fieldtype": "Data", "width": 150},
            {"fieldname": "gender", "label": "Gender", "fieldtype": "Data", "width": 100},
            {"fieldname": "date_of_birth", "label": "Date of Birth", "fieldtype": "Date", "width": 100},
            {"fieldname": "company", "label": "Company", "fieldtype": "Data", "width": 150}
        ]
    elif report_type == "Summary Report":
        return [
            {"fieldname": "month", "label": "Month", "fieldtype": "Data", "width": 100},
            {"fieldname": "opening_balance", "label": "Opening Balance", "fieldtype": "Int", "width": 120},
            {"fieldname": "new_joinees", "label": "New Joins", "fieldtype": "Int", "width": 100},
            {"fieldname": "left_employees", "label": "Left Employees", "fieldtype": "Int", "width": 100},
            {"fieldname": "closing_balance", "label": "Closing Balance", "fieldtype": "Int", "width": 120}
        ]

def get_data(filters, report_type):
    department = filters.get("department")
    
    if report_type == "Head Count Working":
        return get_head_count_data(filters, department)
    elif report_type == "New Joinees List":
        return get_new_joinees_data(filters, department)
    elif report_type == "Left Employees":
        return get_left_employees_data(filters, department)
    elif report_type == "Summary Report":
        return get_summary_data(filters, department)


def get_head_count_data(filters, department):
    end_date = getdate(filters.get("end_date"))

    conditions = ["status = 'Active'"]
    if department:
        conditions.append("department = %(department)s")
    if filters.get("company"):
        conditions.append("company = %(company)s")
    
    where_clause = " AND ".join(conditions)
    
    # Query to get count of all employees including interns
    employee_data = frappe.db.sql(f"""
        SELECT department, employment_type, COUNT(name) as staff_count
        FROM `tabEmployee`
        WHERE {where_clause} AND date_of_joining <= %(end_date)s
        GROUP BY department, employment_type
    """, {
        "end_date": end_date,
        "department": department,
        "company": filters.get("company")
    }, as_dict=True)
    
    # Initialize variables for total count and intern count
    total_count = 0
    intern_count = 0
    
    # Process data to separate interns and calculate total count
    result = []
    for row in employee_data:
        if row['employment_type'] == 'Intern':
            intern_count += row['staff_count']
        else:
            total_count += row['staff_count']
            if not row.get('department'):
                row['department'] = "Not Defined"
            result.append({"department": row["department"], "staff_count": row["staff_count"]})
    
    # Add total count excluding interns to the result
    result.append({"department": "Total (Excluding Interns)", "staff_count": total_count})
    result.append({"department": "Interns", "staff_count": intern_count})
    total_employee = total_count + intern_count
    result.append({"department": "total_employee", "Total_employess": total_employee})

    return result


def get_new_joinees_data(filters, department):
    start_date = getdate(filters.get("start_date"))
    end_date = getdate(filters.get("end_date"))
    conditions = {"status": "Active", "date_of_joining": ["between", [start_date, end_date]]}
    if department:
        conditions["department"] = department
    if filters.get("company"):
        conditions["company"] = filters["company"]
    
    employees = frappe.get_all("Employee", filters=conditions, fields=[
        "employee_name", "employee", "date_of_joining", "department", 
        "gender", "date_of_birth", "company", "designation"
    ])
    
    total_count = len(employees)
    employees.append({"employee_name": "Total", "employee": "", "date_of_joining": "", "department": "", 
                      "gender": "", "date_of_birth": "", "company": "", "designation": "", 
                      "total_count": total_count})

    return employees
def get_left_employees_data(filters, department):
    start_date = getdate(filters.get("start_date"))
    end_date = getdate(filters.get("end_date"))
    conditions = {"status": "Left", "relieving_date": ["between", [start_date, end_date]]}
    if department:
        conditions["department"] = department
    if filters.get("company"):
        conditions["company"] = filters["company"]
    
    employees = frappe.get_all("Employee", filters=conditions, fields=[
        "employee_name", "employee", "relieving_date", "department",
        "gender", "date_of_birth", "company", "designation"
    ])
    
    total_count = len(employees)
    employees.append({"employee_name": "Total", "employee": "", "relieving_date": "", "department": "", 
                      "gender": "", "date_of_birth": "", "company": "", "designation": "", 
                      "total_count": total_count})

    return employees

def get_summary_data(filters, department):
    start_date = getdate(filters.get("start_date"))
    end_date = getdate(filters.get("end_date"))
    
    data = []
    current_date = start_date

    # Calculate the initial opening balance
    opening_balance = get_opening_balance(start_date, department, filters.get("company"))

    while current_date <= end_date:
        month_start = current_date
        month_end = add_months(current_date, 1) - timedelta(days=1)

        new_joinees = count_new_joinees(month_start, month_end, department, filters.get("company"))
        left_employees = count_left_employees(month_start, month_end, department, filters.get("company"))
        closing_balance = opening_balance + new_joinees - left_employees

        data.append({
            "month": formatdate(month_start, "MMMM yyyy"),
            "opening_balance": opening_balance,
            "new_joinees": new_joinees,
            "left_employees": left_employees,
            "closing_balance": closing_balance
        })

        # Set the next month's opening balance to this month's closing balance
        opening_balance = closing_balance
        current_date = add_months(current_date, 1)

    return data

def get_opening_balance(date, department, company):
    conditions = {"status": "Active", "date_of_joining": ["<=", date]}
    if department:
        conditions["department"] = department
    if company:
        conditions["company"] = company
    active_count = frappe.db.count("Employee", conditions)
    
    conditions_left = {"status": "Left", "relieving_date": ["<=", date]}
    if department:
        conditions_left["department"] = department
    if company:
        conditions_left["company"] = company
    left_count = frappe.db.count("Employee", conditions_left)
    
    return active_count - left_count

def count_new_joinees(start_date, end_date, department, company):
    conditions = {"status": "Active", "date_of_joining": ["between", [start_date, end_date]]}
    if department:
        conditions["department"] = department
    if company:
        conditions["company"] = company
    return frappe.db.count("Employee", conditions)

def count_left_employees(start_date, end_date, department, company):
    conditions = {"status": "Left", "relieving_date": ["between", [start_date, end_date]]}
    if department:
        conditions["department"] = department
    if company:
        conditions["company"] = company
    return frappe.db.count("Employee", conditions)

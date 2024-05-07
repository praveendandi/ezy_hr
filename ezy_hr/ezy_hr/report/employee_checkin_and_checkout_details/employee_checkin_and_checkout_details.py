# # Copyright (c) 2024, Ganu Reddy and contributors
# # For license information, please see license.txt

# import frappe


import frappe

def execute(filters=None):
    columns = [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Unit", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "text-align": "Center", "width": 180},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 150},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Duration", "fieldname": "working_hours", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "text-align": "Center", "width": 180},
        {"label": "Actions", "fieldname": "actions", "fieldtype": "Button", "width": 100}
    ]

    data = get_data(filters)
    
    return columns, data



def get_data(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append(f"(date(ec.time) >= '{filters['from_date']}' OR ec.time IS NULL)")
    if filters.get("to_date"):
        conditions.append(f"(date(ec.time) <= '{filters['to_date']}' OR ec.time IS NULL)")
    if filters.get("employee"):
        conditions.append(f"ec.employee = '{filters['employee']}'")
    if filters.get("company"):
        conditions.append(f"e.company = '{filters['company']}'")

    condition_str = " AND ".join(conditions) if conditions else "1=1"

    sql_query = f"""
        SELECT e.employee,e.employee_name,ec.time, e.company, e.date_of_joining, 
               COALESCE(date(ec.time), date(ec.time)) as date,
               MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END) as in_time,
               MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END) as out_time,
               CONCAT(
                   LPAD(
                       FLOOR(
                           ABS(
                               TIMESTAMPDIFF(
                                   MINUTE,
                                   MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END),
                                   MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END)
                               ) / 60
                           )
                       ), 2, '0'
                   ),
                   ':',
                   LPAD(
                       ABS(
                           TIMESTAMPDIFF(
                               MINUTE,
                               MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END),
                               MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END)
                           ) % 60
                       ), 2, '0'
                   )
               ) as working_hours,
               REPLACE(e.department, ' - TPB', '') as department,
               CASE 
                   WHEN MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END) IS NULL AND MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END) IS NULL THEN 'Missing Punches'
                   WHEN MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END) IS NULL THEN 'MI'
                   WHEN MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END) IS NULL THEN 'MO'
                   WHEN TIMESTAMPDIFF(MINUTE,
                                       MIN(CASE WHEN ec.log_type = 'IN' THEN ec.time END),
                                       MAX(CASE WHEN ec.log_type = 'OUT' THEN ec.time END)
                                   ) = 0 THEN ''
                   ELSE 'P'
               END as status
        FROM `tabEmployee` e
        LEFT JOIN `tabEmployee Checkin` ec ON e.name = ec.employee
        WHERE {condition_str}
        GROUP BY e.employee_name, e.company, e.date_of_joining, date(ec.time), e.department
        ORDER BY e.employee_name, date(ec.time)
    """

    data = frappe.db.sql(sql_query, as_dict=1)

    for row in data:
        if not row.get("in_time"):
            row["log_type"] = "IN"
            row["custom_correction"] = "Manual"
        elif not row.get("out_time"):
            row["log_type"] = "OUT"
            row["custom_correction"] = "Manual"
        else:
            row["log_type"] = ""
            row["custom_correction"] = ""

        if not row.get("in_time") or not row.get("out_time"):
            base_url = frappe.utils.get_url()
            row["actions"] = f'<button class="btn btn-secondary btn-sm edit-btn" data-employee="{row["employee"]}" data-in-time="{row["in_time"]}" data-out-time="{row["out_time"]}" data-log-type="{row["log_type"]}" data-custom-correction="{row["custom_correction"]}"><a href="{base_url}/app/employee-checkin/new-employee-checkin?employee={row["employee"]}&log_type={row["log_type"]}&custom_correction=Manual">Edit</a></button>'
        else:
            row["actions"] = ''

    return data

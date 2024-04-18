# Copyright (c) 2024, Ganu Reddy and contributors
# For license information, please see license.txt


import frappe


def execute(filters=None):
    columns = [
        {"label": "Employee ID", "fieldname": "employee", "fieldtype": "Data", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "text-align": "Center", "width": 180},
        {"label": "Date Of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 150},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 150},
        {"label": "First Checkin", "fieldname": "in_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Last Checkout", "fieldname": "out_time", "fieldtype": "Datetime", "width": 180},
        {"label": "Total Working Hours", "fieldname": "working_hours", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "text-align": "Center", "width": 180}
    ]

    data = get_data(filters)
    
    return columns, data





def get_data(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append(f"date(ec.time) >= '{filters['from_date']}'")
    if filters.get("to_date"):
        conditions.append(f"date(ec.time) <= '{filters['to_date']}'")

    condition_str = " AND ".join(conditions) if conditions else "1=1"

    if filters.get("employee"):
        employee_condition = f"ec.employee = '{filters['employee']}' AND "
    else:
        employee_condition = ""

    sql_query = f"""
        SELECT ec.employee as employee, e.employee_name, e.date_of_joining, date(ec.time) as date,
               MIN(ec.time) as in_time,
               (
                   SELECT MIN(time)
                   FROM `tabEmployee Checkin`
                   WHERE employee = ec.employee AND log_type = 'OUT' AND date(time) = date(ec.time)
               ) as out_time,
               CONCAT(
                   LPAD(
                       FLOOR(
                           ABS(
                               TIMESTAMPDIFF(
                                   MINUTE,
                                   MIN(ec.time),
                                   (
                                       SELECT MIN(time)
                                       FROM `tabEmployee Checkin`
                                       WHERE employee = ec.employee AND log_type = 'OUT' AND date(time) = date(ec.time)
                                   )
                               ) / 60
                           )
                       ), 2, '0'
                   ),
                   ':',
                   LPAD(
                       ABS(
                           TIMESTAMPDIFF(
                               MINUTE,
                               MIN(ec.time),
                               (
                                   SELECT MIN(time)
                                   FROM `tabEmployee Checkin`
                                   WHERE employee = ec.employee AND log_type = 'OUT' AND date(time) = date(ec.time)
                               )
                           ) % 60
                       ), 2, '0'
                   )
               ) as working_hours,
               REPLACE(e.department, ' - TPB', '') as department,
               e.company,
               CASE 
                   WHEN MIN(ec.time) IS NOT NULL AND 
                        (
                            SELECT MIN(time)
                            FROM `tabEmployee Checkin`
                            WHERE employee = ec.employee AND log_type = 'OUT' AND date(time) = date(ec.time)
                        ) IS NOT NULL THEN 'Present'
                   WHEN MIN(ec.time) IS NOT NULL AND 
                        (
                            SELECT MIN(time)
                            FROM `tabEmployee Checkin`
                            WHERE employee = ec.employee AND log_type = 'OUT' AND date(time) = date(ec.time)
                        ) IS NULL THEN 'Check-Out Is Missing'
                   ELSE 'Check-In Is Missing'
               END as status
        FROM `tabEmployee Checkin` ec
        JOIN `tabEmployee` e ON ec.employee = e.name
        WHERE {condition_str} AND {employee_condition}ec.time IS NOT NULL
        GROUP BY ec.employee, e.employee_name, e.date_of_joining, date(ec.time), e.department, e.company
        ORDER BY MIN(ec.time) DESC
    """

    data = frappe.db.sql(sql_query, as_dict=1)

    return data


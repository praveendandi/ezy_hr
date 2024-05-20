
import frappe
from frappe.utils import getdate, now_datetime, add_days

@frappe.whitelist()
def get_employee_checkins():
    today = getdate(now_datetime())
    yesterday = add_days(today, -1)
    yesterday_start = yesterday.strftime('%Y-%m-%d') + ' 00:00:00'
    yesterday_end = yesterday.strftime('%Y-%m-%d') + ' 23:59:59'

    # Fetch all employees
    all_employees = frappe.get_all('Employee', fields=['name', 'employee_name', 'company'])

    # Fetch all check-ins for yesterday
    checkins = frappe.get_all(
        'Employee Checkin',
        filters={
            'time': ['between', [yesterday_start, yesterday_end]]
        },
        fields=['name', 'employee', 'time', 'log_type']
    )

    # Group check-ins by employee
    employee_checkins = {}
    for checkin in checkins:
        employee = checkin['employee']
        if employee not in employee_checkins:
            employee_checkins[employee] = {'IN': None, 'OUT': None}
        if checkin['log_type'] == 'IN':
            employee_checkins[employee]['IN'] = checkin['time']
        elif checkin['log_type'] == 'OUT':
            employee_checkins[employee]['OUT'] = checkin['time']

    data = []
    for employee in all_employees:
        emp_id = employee['name']
        unit = employee['company']
        in_time = employee_checkins.get(emp_id, {}).get('IN')
        out_time = employee_checkins.get(emp_id, {}).get('OUT')

        # Skip records with both in_time and out_time missing
        if not in_time and not out_time:
            continue

        status = determine_status(in_time, out_time)

        # Check if an entry already exists
        existing_entry = frappe.db.exists('Employee Missing Checkins Request', {
            'employee': emp_id,
            'date': yesterday
        })

        if not existing_entry:
            try:
                # Create a new Employee Missing Checkins Request document
                doc = frappe.get_doc({
                    'doctype': 'Employee Missing Checkins Request',
                    'employee': emp_id,
                    'unit': unit,
                    'date': yesterday,
                    'in_time': in_time,
                    'out_time': out_time,
                    'status': status
                })
                doc.insert(ignore_permissions=True)
                frappe.db.commit()  # Ensure the transaction is committed to the database
                
                data.append({
                    'employee': emp_id,
                    'unit': unit,
                    'employee_name': employee['employee_name'],
                    'date': yesterday,
                    'in_time': in_time,
                    'out_time': out_time,
                    'status': status
                })
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"Employee Missing Checkins Request already created for {emp_id}")
                print(f"Error creating document for employee {emp_id}: {str(e)}")
        else:
            print(f"Duplicate entry found for employee {emp_id} on date {yesterday}")

    print(data, '/////////////////////////////////')
    return data

def determine_status(in_time, out_time):
    if not in_time:
        return 'MI'
    if not out_time:
        return 'MO'
    return 'P'

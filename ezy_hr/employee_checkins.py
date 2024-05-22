
import frappe
from frappe.utils import getdate, now_datetime, add_days
import sys
import traceback

@frappe.whitelist()
def get_employee_checkins():
    try:
        today = getdate(now_datetime())
        yesterday = add_days(today, -1)
        start_of_month = today.replace(day=1)

        # Fetch all employees
        all_employees = frappe.get_all('Employee', fields=['name', 'employee_name', 'company'])

        # Fetch all check-ins from start of month to yesterday
        checkins = frappe.get_all(
            'Employee Checkin',
            filters={
                'time': ['between', [start_of_month, yesterday]]
            },
            fields=['name', 'employee', 'time', 'log_type']
        )

        # Group check-ins by employee and date
        employee_checkins = {}
        for checkin in checkins:
            employee = checkin['employee']
            checkin_date = getdate(checkin['time']).strftime('%Y-%m-%d')
            if employee not in employee_checkins:
                employee_checkins[employee] = {}
            if checkin_date not in employee_checkins[employee]:
                employee_checkins[employee][checkin_date] = {'IN': None, 'OUT': None}
            if checkin['log_type'] == 'IN':
                employee_checkins[employee][checkin_date]['IN'] = checkin['time']
            elif checkin['log_type'] == 'OUT':
                employee_checkins[employee][checkin_date]['OUT'] = checkin['time']

        data = []
        date = start_of_month
        while date <= yesterday:
            for employee in all_employees:
                emp_id = employee['name']
                unit = employee['company']
                checkin_data = employee_checkins.get(emp_id, {}).get(date.strftime('%Y-%m-%d'), {})
                in_time = checkin_data.get('IN')
                out_time = checkin_data.get('OUT')

                # Only process records with either in_time or out_time missing, but not both present or both missing
                if (in_time and not out_time) or (out_time and not in_time):
                    status = determine_status(in_time, out_time)

                    # Check if an entry already exists for this employee and date
                    existing_entry = frappe.db.exists('Employee Missing Checkins Request', {
                        'employee': emp_id,
                        'date': date
                    })

                    # Create a new Employee Missing Checkins Request document
                    doc = frappe.get_doc({
                        'doctype': 'Employee Missing Checkins Request',
                        'employee': emp_id,
                        'unit': unit,
                        'date': date,
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
                        'date': date,
                        'in_time': in_time,
                        'out_time': out_time,
                        'status': status
                    })
                        

            date = add_days(date, 1)

        return data
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Employee Checkin Details")
def determine_status(in_time, out_time):
    try:
        if not in_time:
            return 'MI'  # Missing In
        if not out_time:
            return 'MO'  # Missing Out
        return 'P'  # Present
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Employee Checkin Details")





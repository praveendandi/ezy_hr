
import frappe
from frappe.utils import getdate, date_diff, add_days
import json

@frappe.whitelist()
def create_absents(data, from_date, to_date):
    try:
        employee_ids = json.loads(data)
        frappe.log_error("final_data", employee_ids, type(employee_ids))

        from_date = getdate(from_date)
        to_date = getdate(to_date)

        if from_date > to_date:
            frappe.throw("From Date cannot be greater than To Date")

        num_days = date_diff(to_date, from_date) + 1
        dates = [add_days(from_date, i) for i in range(num_days)]

        absent_dates = []
        for employee_id in employee_ids:
            frappe.log_error("employee_id",employee_id)
            for date in dates:
                attendance = frappe.get_value('Attendance', {'employee': employee_id.get('name'), 'attendance_date': date}, 'name')
                if not attendance:
                    absent = frappe.get_doc({
                        'doctype': 'Attendance',
                        'employee': employee_id.get('name'),
                        'attendance_date': date,
                        'status': 'Absent',
                        'docstatus': 1
                    })
                    absent.insert()
                    absent_dates.append(date)

        if absent_dates:
            return f"Absent records created for dates: {', '.join([date.strftime('%Y-%m-%d') for date in absent_dates])}"
        else:
            return "Attendance records already exist for all the specified dates"
    except Exception as e:
        frappe.log_error("absent attendance",str(e))
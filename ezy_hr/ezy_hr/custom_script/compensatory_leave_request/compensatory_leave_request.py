import frappe
from frappe.utils import  getdate,add_days
from frappe.utils.data import get_first_day
import sys,traceback

def created_compensatory_leave_base_on_holidays_list():
	try:
	
		check_date = add_days(getdate(), -1)
		# get first day of current month
		holiday_filters = [
			["holiday_date", "=", check_date]
		]
		get_holiday_details = frappe.db.get_value("Holiday",holiday_filters,["holiday_date",'parent', "description"])
		
		if get_holiday_details:

			get_holiday_date,parent,description = get_holiday_details
			
			for each_empl in  frappe. frappe.get_all("Employee",{"status":"Active","holiday_list":parent},["name",'company']):
				is_present_that_day = check_attendance_details(each_empl,get_holiday_date)
				already_comp_leave = check_already_compensatory_leave_is_or_not(each_empl,get_holiday_date)

				if is_present_that_day and not already_comp_leave:
					new_doc = frappe.get_doc({
						"doctype":"Compensatory Leave Request",
						"work_from_date":get_holiday_date,
						"work_end_date":get_holiday_date,
						"company":each_empl.get("company"),
						"employee":each_empl.get("name"),
						"reason":description,
						"leave_type":"Compensatory Off"
					})
					new_doc.save(ignore_permissions=True)
					frappe.db.commit()
	
	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Compensatory Leave")
		
def check_attendance_details(each_empl,get_holiday_date):

	get_result = frappe.db.get_all("Attendance",
				   {
						"attendance_date":["=",get_holiday_date],
						"employee":each_empl.get("name"),
						"docstatus":1,
						"status":"Present"
					},
					["name"]
					)

	if get_result:
		return True
	else:
		return False
	
def check_already_compensatory_leave_is_or_not(each_empl,get_holiday_date):

	get_result = frappe.db.get_value("Compensatory Leave Request",
				   {
						"work_from_date":["=",get_holiday_date],
						"employee":each_empl.get("name")
					},
					["name"]
					)
	
	if get_result:
		return True
	else:
		return False

import frappe
from frappe.utils import  getdate
from frappe.utils.data import get_first_day
import sys,traceback

def created_compensatory_leave_base_on_holidays_list():
	
	to_today = getdate()
	# get first day of current month
	from_date = get_first_day(to_today)

	for each_empl in  frappe.get_all("Employee",["name",'holiday_list','company']):
	
		holiday_filters = [
		["holiday_date", ">=", from_date],
		["holiday_date", "<=", to_today],
		["parent", "=", each_empl.get("holiday_list")]
		]

		for each_date in  frappe.get_all("Holiday",fields=["holiday_date", "description"],filters=holiday_filters):

			is_present_that_day = check_attendance_details(each_empl,each_date)
			already_comp_leave = check_already_compensatory_leave_is_or_not(each_empl,each_date)

			if is_present_that_day and not already_comp_leave:
				new_doc = frappe.get_doc({
					"doctype":"Compensatory Leave Request",
					"work_from_date":each_date.get("holiday_date"),
					"work_end_date":each_date.get("holiday_date"),
					"company":each_empl.get("company"),
					"employee":each_empl.get("name"),
					"reason":each_date.get("description"),
					"leave_type":"Compensatory Off"
				})
				new_doc.save(ignore_permissions=False)
				frappe.db.commit()

		
def check_attendance_details(each_empl,each_date):

	get_result = frappe.db.get_all("Attendance",
				   filters={
						"attendance_date":["Between",[each_date.get("holiday_date"),each_date.get("holiday_date")]],
						"employee":each_empl.get("name"),
						"docstatus":1,
						"status":"Present"
					},
					fields = ['employee',"status",'attendance_date','company']
					)

	if get_result:
		return True
	else:
		return False
	
def check_already_compensatory_leave_is_or_not(each_empl,each_date):

	get_result = frappe.db.get_all("Compensatory Leave Request",
				   filters={
						"work_from_date":["Between",[each_date.get("holiday_date"),each_date.get("holiday_date")]],
						"employee":each_empl.get("name")
					},
					fields = ['employee','work_from_date',"work_end_date",'custom_unit']
					)
	
	if get_result:
		return True
	else:
		return False
	
@frappe.whitelist()
def background_job_for_compensatory_leave():
	try:
		frappe.enqueue(
			method = "ezy_hr.ezy_hr.custom_script.compensatory_leave_request.compensatory_leave_request.created_compensatory_leave_base_on_holidays_list",
			queue="long",
			timeout="3600",
			is_async=True,
			job_id="Compensatory Leave Creation",
			enqueue_after_commit=True,
		)

	except Exception as e:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		frappe.log_error("line No:{}\n{}".format(exc_tb.tb_lineno, traceback.format_exc()), "Compensatory Leave")

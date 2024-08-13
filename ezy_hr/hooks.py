app_name = "ezy_hr"
app_title = "Ezy HR"
app_publisher = "Ganu Reddy"
app_description = "Ezy HR"
app_email = "ganu.b@caratred.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ezy_hr/css/ezy_hr.css"
# app_include_js = "/assets/ezy_hr/js/ezy_hr.js"

# include js, css files in header of web template
web_include_css = "/assets/ezy_hr/css/custom_styles.css"
# web_include_js = "/assets/ezy_hr/js/ezy_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ezy_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Travel Request" : "public/js/traval_request_to_claim.js",
              "Payroll Entry":"public/js/employee_separeted.js",
              "Employee":"ezy_hr/custom_script/employee/employee.js",
            #   "Employee":"public/js/salary_hide.js",
              "Employee Promotion":"public/js/employee_promotion.js",
              "Appointment Letter":"ezy_hr/custom_script/appointment_letter/appointment_letter.js",
              "Compensatory Leave Request":"public/js/compensatory_leave.js",
              "Employee Resignation":"public/js/employee_resignation.js"
              
              }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ezy_hr/public/icons.svg"

# Home Pages
# ----------


fixtures = [

    "Role Profile",
    "Role",
    "Workflow",
    "Workflow State",
    "Custom HTML Block"
]

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ezy_hr.utils.jinja_methods",
# 	"filters": "ezy_hr.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ezy_hr.install.before_install"
# after_install = "ezy_hr.install.after_install"
after_install = "ezy_hr.setup.setup_fixtures"


# Uninstallation
# ------------

# before_uninstall = "ezy_hr.uninstall.before_uninstall"
# after_uninstall = "ezy_hr.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ezy_hr.utils.before_app_install"
# after_app_install = "ezy_hr.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ezy_hr.utils.before_app_uninstall"
# after_app_uninstall = "ezy_hr.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ezy_hr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
    "Shift Type": "ezy_hr.ezy_hr.create_attendance.ShiftType",
    "Payroll Entry":"ezy_hr.payroll_entry.custom_class.PayrollEntry",
    "Employee Transfer":"ezy_hr.ezy_hr.custom_script.employee_transfer.employee_transfer.EmployeeTransfer"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
    "Job Applicant":{
        "on_update":"ezy_hr.job_applicant.new_job_condidate_application"
    },
    "Pre-Offer Document":{
        "on_update":"ezy_hr.pre_offer_document.creating_pre_offer_document"
        },
    "Pre-joining document":{
        "on_update":"ezy_hr.pre_joining_document.creating_new_pre_joining_document"
    },
    "Personal Files":{
        "on_update":"ezy_hr.personl_file.create_personal_file_through_employee"
    },
    "Employee":{
        # /home/caratred/Desktop/frappe15/apps/ezy_hr/ezy_hr/ezy_hr/custom_script/employee/employee.py
        # "on_update":"ezy_hr.ezy_hr.custom_script.employee.employee.after_update",
        "on_update":"ezy_hr.ezy_hr.custom_script.employee.employee.create_salary_structure_through_employee",
        "before_save":"ezy_hr.employee_biometric.update_employee_biometric_id",
        
        
    },
    "Leave Application":{
        "on_update":"ezy_hr.ezy_hr.events.weekoff_limit_for_month"
    },
    "Employee Promotion":{
        "on_submit":"ezy_hr.custom_salary.update_and_create_salary",
        "validate": "ezy_hr.custom_salary.check_effective_date",
    },
    "Salary Slip":{
        "before_insert":"ezy_hr.addition_earning_public_ho.cancel_addition_salary",
        "after_insert":"ezy_hr.addition_earning_public_ho.creating_additional_earn_and_com_off",
        "on_cancel":"ezy_hr.addition_earning_public_ho.cancel_addition_salary",
        "on_trash":"ezy_hr.addition_earning_public_ho.cancel_addition_salary",
    },
    "Employee Checkin":{
        "after_insert":"ezy_hr.ezy_hr.custom_script.attendance.attendance.get_attendance"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "0 0 * * *": [
            "ezy_hr.employee_checkins.get_employee_checkins",
            "ezy_hr.employee_seperation_details.fetch_employees_with_upcoming_relieving"
        ],
        "0 10 * * *": [
            "ezy_hr.ezy_hr.custom_script.common_script.notifications.send_checkins_notification"
        ]
    },
    "daily": [
		"ezy_hr.ezy_hr.events.flexi_weekoff"
	],

    "hourly": [
		"ezy_hr.ezy_hr.create_attendance.process_auto_attendance_for_all_shifts",
        "ezy_hr.ezy_hr.doctype.ezyhrms_transaction.ezyhrms_transaction.get_checkin_alert"
	],
}


# Testing
# -------

# before_tests = "ezy_hr.install.before_tests"

# Overriding Methods
# ------------------------------

# override_whitelisted_methods = {
# 	"hrms.hr.doctype.job_offer.job_offer.make_employee": "ezy_hr.ezy_hr.custom_script.employee.employee.custom_api_for_make_employee_through_job_off"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ezy_hr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ezy_hr.utils.before_request"]
# after_request = ["ezy_hr.utils.after_request"]

# Job Events
# ----------
# before_job = ["ezy_hr.utils.before_job"]
# after_job = ["ezy_hr.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ezy_hr.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


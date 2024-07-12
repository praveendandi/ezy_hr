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
              "Employee Promotion":"public/js/employee_promotion.js",
              "Appointment Letter":"ezy_hr/custom_script/appointment_letter/appointment_letter.js"
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
    {
        "dt":
            "Custom Field",
            "filters":[[
                "name",
                "in",
                {
                    "Employee-custom_work_location_type",
                    "Employee-custom_current_work_address",
                    "Employee-custom_height",
                    "Employee-custom_weight",
                    "Employee-custom_aadhaar_card_detail",
                    "Employee-custom_name_as_per_aadhar",
                    "Employee-custom_column_break_bzcj6",
                    "Employee-custom_aadhar_no",
                    "Employee-custom_voter_id_detail",
                    "Employee-custom_voter_id_no",
                    "Employee-custom_column_break_t3aj3",
                    "Employee-custom_name_as_per_voter_id",
                    "Employee-custom_disability",
                    "Employee-custom_languages",
                    "Employee-custom_language",
                    "Employee-custom_esic_no",
                    "Employee-custom_group_doj",
                    "Employee-custom_section_break_9smln",
                    "Employee-custom_nationality",
                    "Employee-custom_official_mobile_no",
                    "Employee-custom_address_line_1",
                    "Employee-custom_address_line_2",
                    "Employee-custom_address_line_3",
                    "Employee-custom_city_",
                    "Employee-custom_state",
                    "Employee-custom_pin_code",
                    "Employee-custom_permanent_address_line_1",
                    "Employee-custom_permanent_address_line_2",
                    "Employee-custom_permanent_address_line_3",
                    "Employee-custom_permanent_city",
                    "Employee-custom_permanent_state",
                    "Employee-custom_permanent_pin",
                    "Employee-custom_email_id",
                    "Employee Health Insurance-custom_mediclaim_no",
                    "Employee Health Insurance-custom_spouse_name",
                    "Employee Health Insurance-custom_depandent_details",
                    "Employee Health Insurance-custom_dependent_1_name",
                    "Employee Health Insurance-custom_relation_1",
                    "Employee Health Insurance-custom_date_of_birth_1",
                    "Employee Health Insurance-custom_column_break_wx5es",
                    "Employee Health Insurance-custom_dependent_2_name",
                    "Employee Health Insurance-custom_relation_2",
                    "Employee Health Insurance-custom_date_of_birth_2",
                    "Employee-custom_nominee_details__pf",
                    "Employee-custom_name_of_nominee",
                    "Employee-custom_relationship_with_nominee",
                    "Employee-custom_nominee_date_of_birth",
                    "Employee-custom_section_break_2telh",
                    "Employee-custom_nominee_address_line_1",
                    "Employee-custom_nominee_district",
                    "Employee-custom_nominee_pin_code",
                    "Employee-custom_column_break_rdtab",
                    "Employee-custom_nominee_address_line_2",
                    "Employee-custom_nominee_state",
                    "Employee-custom_nominee_gratuity_details",
                    "Employee-custom_name_of_nominee_1",
                    "Employee-custom_relationship_with_nominee_2",
                    "Employee-custom_date_of_birth_3",
                    "Employee-custom_section_break_6knts",
                    "Employee-custom_nominee_address_line_3",
                    "Employee-custom_nominee_district_1",
                    "Employee-custom_nominee_pin_code_1",
                    "Employee-custom_column_break_qgspz",
                    "Employee-custom_nominee_address_line_4",
                    "Employee-custom_nominee_state_2",
                    "Department-custom_outlet",
                    "Department-custom_cost_centre_code",
                    "Department-custom_department_code",
                    "Department-custom_gl_code",
                    "Employee Health Insurance-custom_column_break_9pzcf",
                    "Employee Health Insurance-custom_father_name",
                    "Employee Health Insurance-custom_mother_name",
                    "Employee Health Insurance-custom_child_first",
                    "Employee Health Insurance-custom_child_second",
                    "Employee-custom_employment_status",
                    "Job Applicant-custom_employee_id",
                    "Job Applicant-custom_eligibility_criteria",
                    "Job Applicant-custom_total_overall_work_experience",
                    "Job Applicant-custom_column_break_dxdne",
                    "Job Applicant-custom_unit_experience_",
                    "Job Applicant-custom_current_gross_salary",
                    "Job Applicant-custom_reference_details",
                    "Job Applicant-custom_reference_name",
                    "Job Applicant-custom_mobile_no",
                    "Job Applicant-custom_column_break_66ika",
                    "Job Applicant-custom_email_id",
                    "Job Applicant-custom_previous_company",
                    "Job Applicant-custom_reference_second_details",
                    "Job Applicant-custom_reference_second_name",
                    "Job Applicant-custom_reference_mobile_no",
                    "Job Applicant-custom_column_break_8bhjh",
                    "Job Applicant-custom_reference_second_email_id",
                    "Job Applicant-custom_reference_previous_second_company",
                    "Job Applicant-custom_reference_check_authorisation_letter",
                    "Job Applicant-custom_reference_check",
                    "Employee-custom_salary_breakdown",
                    "Employee-custom_earnings",
                    "Employee-custom_deductions",
                    "Job Applicant-custom_current_unit",
                    "Job Applicant-custom_receiving_unit",
                    "Job Opening-custom_internal_job_posting",
                    "Job Applicant-custom_section_break_yac9f",
                    "Job Applicant-custom_external_job_posting",
                    "Job Applicant-custom__internal_job_posting",
                    "Job Applicant-custom_current_ctc",
                    "Job Applicant-custom_aadhar_no",
                    "Employee-custom_gross_amount",
                    "Employee-custom_income_tax_slab",
                    "Employee-custom_tax_slabe_and_effective",
                    "Employee-custom_effective_date",
                    "Employee-custom_select_break_of_earning_and_deduction",
                    "Salary Detail-custom_employee_condition",
                    "Employee Checkin-custom_correction",
                    "Employee-custom_prejoining_document",
                    "Employee-custom_job_applicant_email_1",
                    "Employee-custom_aadhar_no_1",
                    "Employee-custom_unit_2",
                    "Employee-custom_document_attach_details_1",
                    "Employee-custom_formal_photographs_with_white_background_soft_copy",
                    "Employee-custom_date_of_birth_proof",
                    "Employee-custom_certificate_in_support_oeducational__professional",
                    "Employee-custom_employment_certificate_of_previous_employer",
                    "Employee-custom_from_1612ba_of_previous_employer",
                    "Employee-custom_column_break_eckhc",
                    "Employee-custom_applicant_name_1",
                    "Employee-custom_mobile_no_1",
                    "Employee-custom_creation_date_1",
                    "Employee-custom_column_break_hi5ac",
                    "Employee-custom_proof_details",
                    "Employee-custom_photo_id_proof_address_proof",
                    "Employee-custom_pan_card",
                    "Employee-custom_aadhar_card",
                    "Employee-custom_third_slip",
                    "Employee-custom_pre_joining_documents_details",
                    "Employee-custom_column_break_7fdnl",
                    "Employee-custom_first_slip",
                    "Employee-custom_payslips_of_last_three_months",
                    "Employee-custom_current_ctc_structure",
                    "Employee-custom_current_ctc_structure_detail",
                    "Employee-custom_creation_date",
                    "Employee-custom_mobile_no",
                    "Employee-custom_applicant_name",
                    "Employee-custom_column_break_ne9br",
                    "Employee-custom_unit",
                    "Employee-custom_aadhar_no_",
                    "Employee-custom_job_applicant_email",
                    "Employee-custom_preoffer_document",
                    "Employee-custom_preoffer_document_",
                    "Employee Transfer-custom_new_unit",
                    "Payroll Employee Detail-custom_separation_id",
                    "Payroll Employee Detail-custom_status",
                    "Payroll Entry-custom_validate_employee_seperation",
                    "Payroll Entry-custom_uncompleted_seperations",
                    "Leave Type-custom_flexi_week_off",
                    "Leave Type-custom_leaves",
                    "Leave Type-custom_unit",
                    "Leave Type-custom_holiday_list",
                    "Leave Type-custom_unit_holiday_list",
                    "Leave Type-custom_select_holiday_type",
                    "Leave Allocation-custom_leave_allocation_date_and_description",
                    "Leave Ledger Entry-custom_reason_date_",
                    "Employee Promotion-custom_effective_date",
                    "Employee Promotion-custom_current_gross_amount",
                    "Employee Promotion-custom_new_gross_amount",
                    "Employee Promotion-custom_earnings_section",
                    "Employee Promotion-custom_earnings_detail",
                    "Employee Promotion-custom_previous_effective_date",
                    "Employee-custom_apply_for_nfh_wages",
                    "Salary Slip-custom_payroll_cost_center_",
                    "Job Offer-custom_level",
                    "Job Offer-custom_department",
                    "Salary Slip-custom_ifsc",
                    "Salary Slip-custom_esi_reason",
                    "Salary Slip-custom_reason_for_esi",
                    "Employee-custom_applicable_for_actual_pf",
                    "Job Offer-custom_salary_breakup",
                    "Job Offer-custom_earning",
                    "Job Offer-custom_deducations",
                    "Job Offer-custom_gross_amount",
                    "Employee-custom_leave_policy",
                    "Payroll Employee Detail-custom_manual_hold",
                    "Payroll Employee Detail-custom_reason_for_salary_hold",
                },
                
            ]]
    }
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
    "Payroll Entry":"ezy_hr.payroll_entry.custom_class.PayrollEntry"
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
        "on_update":["ezy_hr.custom_salary.create_salary_structure_through_employee",
                     "ezy_hr.ezy_hr.custom_script.employee.employee.assign_leave_policy"],
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
        "on_update":"ezy_hr.ezy_hr.custom_script.attendance.attendance.get_attendance"
    }
}

scheduler_events = {
    "cron": {
        "0 0 * * *": [
            "ezy_hr.employee_checkins.get_employee_checkins",
            "ezy_hr.employee_seperation_details.fetch_employees_with_upcoming_relieving"
        ]
    },
    "daily": [
		"ezy_hr.ezy_hr.events.flexi_weekoff"
	],

    "hourly": [
		"ezy_hr.ezy_hr.create_attendance.process_auto_attendance_for_all_shifts"
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


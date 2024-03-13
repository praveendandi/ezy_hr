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
# web_include_css = "/assets/ezy_hr/css/ezy_hr.css"
# web_include_js = "/assets/ezy_hr/js/ezy_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ezy_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
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
                    "Employee-custom_section_break_pe7u5",
                    "Employee-custom_father_name",
                    "Employee-custom_column_break_ycpbb",
                    "Employee-custom_mother_name",
                    "Employee-custom_aadhaar_card_detail",
                    "Employee-custom_name_as_per_aadhar",
                    "Employee-custom_column_break_bzcj6",
                    "Employee-custom_aadhar_no",
                    "Employee-custom_voter_id_detail",
                    "Employee-custom_voter_id_no",
                    "Employee-custom_column_break_yk648",
                    "Employee-custom_name_as_per_voter_id",
                    "Employee-custom_disability",
                    "Employee-custom_languages",
                    "Employee-custom_language",
                    "Employee-custom_esic_no",
                    "Employee-custom_group_doj",
                    "Employee-custom_section_break_9smln"
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

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ezy_hr.tasks.all"
# 	],
# 	"daily": [
# 		"ezy_hr.tasks.daily"
# 	],
# 	"hourly": [
# 		"ezy_hr.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ezy_hr.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ezy_hr.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ezy_hr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ezy_hr.event.get_events"
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


from . import __version__ as app_version

app_name = "electra"
app_title = "Electra"
app_publisher = "Abdulla"
app_description = "Electra"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "abdulla.pi@groupteampro.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/electra/css/electra.css"
# app_include_js = "/assets/electra/js/electra.js"
app_include_js = [
            "/assets/electra/js/linkselector.js",
                ]
# include js, css files in header of web template
# web_include_css = "/assets/electra/css/electra.css"
# web_include_js = "/assets/electra/js/electra.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "electra/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/quotation.js"}
doctype_list_js = {"Lead" : "public/js/lead_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "electra.install.before_install"
# after_install = "electra.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "electra.notifications.get_notification_config"

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
	# "Employee":"electra.overrides.CustomEmployee",
	# "ToDo": "custom_app.overrides.CustomToDo",\

# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		# "on_update_"electra.custom.employee_number",
		"on_trash": "electra.utils.manpower_avg_cost_calculation",
		"after_insert": [
			"electra.custom.visa_creation",
			"electra.utils.manpower_avg_cost_calculation",
			],
	},
	"Landed Cost Voucher": {
		"on_submit": "electra.custom.create_lcv_je",
		"on_cancel": "electra.custom.cancel_lcv_je",
	},
	"Leave Application": {
		"after_insert": "electra.custom.rejoin_form_creation",
	},
	"Project":{
		"on_update" : "electra.custom.create_tasks",
		# "after_insert" : "electra.utils.create_project_warehouse"
	},
    "Leave Application":{
		"after_insert" : "electra.custom.alert_to_substitute"
	},
	"Cost Estimation":{
		"after_insert" : "electra.custom.amend_ce"
	},
	# "Project Budget":{
	# 	"after_insert" : "electra.custom.amend_pb"
	# },
	# "Opportunity":{
	# 	"validate":"electra.utils.validate_opportunity_sow"
	# },
	"Quotation":{
		"after_insert":"electra.utils.add_quotation_ce",
		"on_cancel":"electra.custom.cancel_ce"
	},
	"Sales Order":{
		"validate":"electra.utils.validate_sow",
		"on_submit": "electra.utils.create_project_from_so",
		# "on_cancel":"electra.custom.cancel_pb"
		# "after_save":"electra.custom.set_default_warehouse"
	},
	"Item":{
		"after_insert":"electra.utils.item_default_wh"
	},
	"Delivery Note":{
		"on_submit":"electra.utils.submit_dummy_dn"
	},
	"Vehicle Maintenance Check List":{
		"on_update":"electra.custom.isthimara_exp_mail"
	},
	"Sales Invoice":{
		"on_submit":"electra.custom.create_payment_entry"
		# "on_update_after_submit":"electra.custom.get_dn_list_sales_invoice",
		# "onload":"electra.custom.get_due_date"
	},
	# "Project Day Plan":{
	# 	"before_save":"electra.custom.get_all_projects"
	# },
	# "Stock Transfer":{
	# 	"on_update":"electra.electra.doctype.stock_transfer.stock_transfer.cancel_stock_request"
	# },
	'Resignation Form':{
		'on_submit':'electra.utils.update_employee_status'
	},
	'Job Offer':{
		'on_update':'electra.custom.employee_number'
	}
}



# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"electra.utils.cron_test"
		]
	},
	"daily": [
		"electra.alerts.update_lcm_due_status"
	],
# 	"daily": [
# 		"electra.tasks.daily"
# 	],
# 	"hourly": [
# 		"electra.tasks.hourly"
# 	],
# 	"weekly": [
# 		"electra.tasks.weekly"
# 	]
	"monthly": [
		"electra.custom.isthimara_exp_mail"
	]
}

# Testing
# -------

# before_tests = "electra.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.search.search_widget": "electra.electra.api.search_widget",
	"frappe.utils.pdf.get_pdf":"electra.utils.pdf.get_pdf"
}

# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "electra.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"electra.auth.validate"
# ]

fixtures = ['Custom Field','Client Script','Workspace','User Permission']

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
            "https://maps.googleapis.com/maps/api/js?sensor=false&libraries=places&key=AIzaSyAdaNNXhTh13TRLiZjSa9YYp66gNNj9aZ8"
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
doctype_js = {"Sales Invoice" : "public/js/sales_invoice.js"}
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
# boot_session = "electra.utils.add_company_to_session_defaults"
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
		"validate": "electra.custom.inactive_employee",
	},
    "Material Request" : {
        "after_insert":"electra.custom.get_hod_values"
	},
	"Landed Cost Voucher": {
		"on_submit": "electra.custom.create_lcv_je",
		"on_cancel": "electra.custom.cancel_lcv_je",
	},
    "Payment Entry":{
        # "on_submit":"electra.utils.update_outstanding_without_retention"
	},
	# "Leave Application": {
	# 	"after_insert": "electra.custom.rejoin_form_creation",
	# },
	# "Customer":{
	# 	"after_insert": "electra.custom.cred_limit_upload"
	# },
	"Additional Salary": {
		"on_submit": "electra.custom.salary_payroll",
	},

    # "Sales Order":
	# {
    #     "before_save": "electra.custom.validate",
    # },
	"Project":{
		"after_insert": ["electra.custom.get_po_name","electra.utils.create_project_warehouse","electra.custom.create_tasks"]
	},
	# "Leave Extension": {
    #     "on_submit": "electra.custom.on_update_le"
    # },
	"Loan Application":{
		"validate":"electra.custom.check_loan_amount"
        
	},
    # "Leave Application":{
	# 	"after_insert" : "electra.custom.alert_to_substitute",
	# },
	"Cost Estimation":{
		"after_insert" : "electra.custom.amend_ce"
	},
	"Project Budget":{
		"after_insert" : "electra.custom.amend_pb"
	},
	# "Opportunity":{
	# 	"validate":"electra.utils.validate_opportunity_sow"
	# },
	"Quotation":{
		"after_insert":"electra.utils.add_quotation_ce",
	},
	"Sales Order":{
		"validate":["electra.utils.validate_sow","electra.utils.restrict_general_item_so"],
		"on_submit": "electra.utils.create_project_from_so",
		"after_insert": "electra.custom.projectbudget_name",
		"on_cancel":"electra.custom.sales_order_cancel",
        "on_update_after_submit":"electra.custom.update_bidding_price",
        "before_submit":"electra.custom.is_si_approved"
		# "on_cancel":"electra.custom.cancel_pb"
		# "after_save":"electra.custom.set_default_warehouse"
	},
	"Item":{
		"after_insert":"electra.utils.item_default_wh"
	},
	"Delivery Note":{
        "validate":["electra.utils.restrict_general_item_dn"],
        "on_cancel":"electra.custom.on_cancel_dn",
		"on_submit":["electra.utils.submit_dummy_dn","electra.custom.create_stock_out"],
		"before_submit":"electra.custom.is_dummy_dn_approved"
	},
	"Vehicle Maintenance Check List":{
		"on_update":"electra.custom.isthimara_exp_mail"
	},
	"POS Invoice":{
		"on_submit":"electra.custom.automate_pos"
	},
	"Sales Invoice":{
		"on_submit":[
		# 	"electra.custom.create_payment_entry",
			"electra.custom.update_stock_after_return",
			],
		# "before_submit": "electra.custom.update_ret_out",
		"on_update":["electra.custom.update_ret_out","electra.utils.set_income_account","electra.custom.invoice"],
					
		"validate":["electra.utils.set_income_account","electra.utils.restrict_general_item_si","electra.custom.update_return_doc"],
		"after_save":"electra.custom.sales_invoice_remarks",
		"on_cancel":"electra.custom.invoice_cancel",

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
	# 'Job Offer':{
	# 	'on_update':'electra.custom.employee_number'
	# }
}



# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"electra.utils.cron_test"
		],
        "0 2 * * * *": [
			"electra.custom.monthly_expiry_doc"
		],
		"30 10 * * *": [
			"electra.custom.mark_absent"
		]
	},
	"daily": [
		"electra.alerts.update_lcm_due_status"
		# "electra.custom.update_employee_salary"
	],
# 	"daily": [
# 		"electra.tasks.daily"
# 	],
	"hourly": [
		"electra.utils.reset_general_entry_purchase_rate"
	],
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
	# "frappe.utils.pdf.get_pdf":"electra.utils.pdf.get_pdf"
}

override_doctype_class = {
	"Employee Separation":"electra.overrides.CustomEmployeeSeparation"
}

jinja = {
	"methods": [
		"electra.utils.get_dns",
		"electra.utils.get_sos",
		"electra.electra.doctype.multi_project_day_plan.multi_project_day_plan.get_child_table_data",
		"electra.electra.doctype.multi_project_day_plan.multi_project_day_plan.get_driver_table_data",
		# "electra.custom.get_sales_person_invoice",
        "electra.custom.get_sales_person",
		"electra.custom.get_accounts_ledger",
        "electra.custom.get_items",
		"electra.utils.actual_vs_budgeted",
		"electra.utils.work_order_brief_report",
		"electra.utils.work_order_detailed_report",
		"electra.custom.pay_consolidated_req",
		"electra.custom.return_total_amt",
        "electra.custom.scope_of_work",
        "electra.electra.doctype.cost_estimation.cost_estimation.get_data"
	]
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

fixtures = ['Custom Field','Client Script','Workspace','User Permission','Print Format']

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
		# "on_update":"electra.custom.employee_number",
		"on_trash": ["electra.utils.manpower_avg_cost_calculation","electra.custom.delete_employee_leave_allocation"],
		"after_insert": [
			"electra.custom.visa_creation",
			"electra.utils.manpower_avg_cost_calculation",
			"electra.custom.create_annual_leave_allocation_for_new_joinees"
            
			],
		"validate": "electra.custom.inactive_employee",
	},
	# "Rejoining Form":{
	# 	"on_submit": "electra.utils.rejoining_date_validation",
	# },
	"Landed Cost Voucher": {
		"on_submit": "electra.custom.create_lcv_je",
		"on_cancel": "electra.custom.cancel_lcv_je",
        # "after_insert":"electra.custom.get_previous_purchase_rate"
	},
    "Payment Entry":{
		"on_submit" : ["electra.custom.update_advance_percentage"],
		"on_cancel" : "electra.custom.update_advance_percentage",
		"validate": "electra.custom.validate_posting_date_for_pe"
        # "after_insert":"electra.custom.update_pay_name",
        # "on_submit":"electra.utils.update_outstanding_without_retention"
	},
    "Advance Invoice":{
        "after_insert":["electra.custom.update_advance_amount"],
        "on_submit":"electra.custom.create_new_journal_entry",
        "on_cancel":"electra.custom.cancel_journal_entry",
	},
    "Retention Invoice":{
        "after_insert":["electra.custom.update_retention_amount"],
        "on_submit":"electra.custom.create_new_journal_entry_retention",
        "on_cancel":"electra.custom.cancel_journal_entry_retention",
	},
    "Leave Salary": {
		"before_save": "electra.custom.gratuity_calculation",
	},
    
	# "Leave Application": {
	# 	"after_insert": "electra.custom.rejoin_form_creation",
	# },
	"Customer":{
		"after_insert": "electra.utils.create_existing",
		"validate":"electra.custom.avoid_duplicate_name"
	},
    "Supplier":{
		"after_insert": "electra.utils.create_existing"
	},
	"Additional Salary": {
		"on_submit": "electra.custom.salary_payroll",
	},

    # "Sales Order":
	# {
    #     "before_save": "electra.custom.validate",
    # },
	"Project":{
		"after_insert": ["electra.custom.get_po_name","electra.utils.create_project_warehouse","electra.custom.create_tasks"],
		"on_trash": "electra.utils.pe_on_trash"
	},
	# "Leave Extension": {
    #     "on_submit": "electra.custom.on_update_le"
    # },
	# "Loan Application":{
	# 	"validate":"electra.custom.check_loan_amount"
	# },
    # "Leave Application":{
	# 	"after_insert" : "electra.custom.alert_to_substitute",
	# },
	"Cost Estimation":{
		"after_insert" : "electra.custom.amend_ce",
		"on_submit": "electra.custom.create_item_on_ce_submit",
        "on_trash":"electra.custom.linked_cesow_delete"
	},
    "Item Price":{
       "validate":"electra.custom.validate_item_price" 
	},
	"CE SOW":{
		"validate":"electra.custom.validate_item"
	},
	"PB SOW":{
		"validate":"electra.custom.validate_item_pb"
	},
	"Project Budget":{
		"after_insert" : "electra.custom.amend_pb",
		# "on_submit": "electra.electra.doctype.project_budget.project_budget.udpate_total_cost_section"
	},
    "Material Request":{
        "on_submit":["electra.custom.mr_qty","electra.utils.update_mr_qty_in_so"],
        "on_cancel":["electra.utils.update_mr_qty_in_so_cancel"]
	},
	# "Opportunity":{
	# 	"validate":"electra.utils.validate_opportunity_sow"
	# },
	"Quotation":{
		"after_insert":"electra.utils.add_quotation_ce",
        "validate":"electra.custom.check_cut_off_amount"
	},
	"Sales Order":{
		"validate":["electra.utils.validate_sow","electra.utils.restrict_general_item_so"],
		# "on_submit": ["electra.utils.create_project_from_so"],
		"on_submit": ["electra.utils.create_project_from_so","electra.utils.update_pb_sow"],
		"after_insert": "electra.custom.projectbudget_name",
		"on_cancel":"electra.custom.sales_order_cancel",
        "on_update_after_submit":["electra.custom.update_bidding_price","electra.utils.update_pb_sow"],
        # "on_update_after_submit":["electra.custom.update_bidding_price"],
        "before_submit":["electra.custom.is_si_approved","electra.custom.validate_project_budget"],
		# "on_cancel":"electra.custom.cancel_pb"
		# "after_save":"electra.custom.set_default_warehouse"
        "on_trash": "electra.custom.delete_warehouse_from_so",
	},
    "Appraisal": {
        "validate":"electra.custom.add_description_in_appraisal",
	},
	"Item":{
		"after_insert":"electra.utils.item_default_wh"
	},
	"Delivery Note":{
        "validate":["electra.utils.restrict_general_item_dn","electra.utils.update_credit_limit"],
        "on_cancel":"electra.custom.on_cancel_dn",
		"on_submit":["electra.utils.submit_dummy_dn","electra.custom.create_stock_out"],
		"before_submit":"electra.custom.is_dummy_dn_approved"
	},
	"Delivery Note WIP":{
        "on_cancel":["electra.custom.on_cancel_dn","electra.custom.update_so_delivered_qty"],
		"on_submit":["electra.custom.project_delivery","electra.custom.update_per_delivered_in_so"],
	},
	"POS Invoice":{
		"on_submit":"electra.custom.automate_pos"
	},
    "Purchase Order":{
        "validate":"electra.custom.check_approved_supplier"
	},
	"Sales Invoice":{
		"on_submit":[
			"electra.custom.validation_on_submission",
		# 	"electra.custom.create_payment_entry",
			# "electra.custom.create_ret_je",
			"electra.custom.update_stock_after_return",
            "electra.custom.update_return_doc",
            # "electra.custom.check_approved_by_finance",
			"electra.custom.update_stock_on_si_new",
            "electra.custom.update_gl_internal_customer",
			"electra.custom.update_net_total"
			],
		# "before_submit": "electra.custom.update_ret_out",
		"on_update":["electra.custom.update_ret_out","electra.utils.set_income_account"],
		"before_cancel":"electra.custom.cancel_ret_je",
		"validate":["electra.utils.set_income_account","electra.utils.restrict_general_item_si","electra.utils.update_credit_limit"],
		"after_save":"electra.custom.sales_invoice_remarks",
		"on_cancel":[
			"electra.custom.validation_on_cancellation",
			"electra.custom.invoice_cancel",
			"electra.custom.cancel_stock_on_si",
			"electra.custom.cancel_dn_on_si_cancel",
			# "electra.custom.check_current_user_role"
		],
        "after_insert":"electra.custom.update_invoice_number"

		# "on_update_after_submit":"electra.custom.get_dn_list_sales_invoice",
		# "onload":"electra.custom.get_due_date"
	},
	"Stock Entry":{
        "on_submit":["electra.utils.update_finished_goods","electra.utils.update_finished_goods_in_project_budget","electra.utils.update_finished_goods_in_so","electra.utils.update_finished_goods_in_cesow"],
        "on_cancel":["electra.utils.update_qty_cancel","electra.utils.update_qty_in_pbsow_cancel","electra.utils.update_qty_in_so_cancel"]
	},
	# "Project Day Plan":{
	# 	"before_save":"electra.custom.get_all_projects"
	# },
	# "Stock Transfer":{
	# 	"on_update":"electra.electra.doctype.stock_transfer.stock_transfer.cancel_stock_request"
	# },
	"Stock Request":{
		"validate":"electra.custom.update_req_qty",
        "on_submit":["electra.custom.update_stock_qty"],
        "on_cancel":["electra.custom.update_stock_qty_cancel"]
	},
    # "Stock Transfer":{
    #     "on_submit":"electra.custom.set_submitted_date"
	# },
    # "Stock Confirmation":{
    #     "on_submit":"electra.custom.set_submitted_date_con"
	# },
    
	"Stock Confirmation":{
        "on_cancel":"electra.custom.cancel_purchase_invoice"
	},
    "Stock Transfer":{
        "on_cancel":"electra.custom.cancel_sales_invoice"
	},
	'Resignation Form':{
		'on_submit':'electra.utils.update_employee_status'
	},
	# 'Job Offer':{
	# 	'on_update':'electra.custom.employee_number'
	# }
    'Loan Repayment Schedule':{
		'on_submit':'electra.custom.create_additional_salary',
	},
}



# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		# "0/15 * * * *": [
		# 	"electra.utils.cron_test"
		# ],
        "0 2 * * * *": [
			"electra.custom.monthly_expiry_doc"
		],
		"30 10 * * *": [
			"electra.custom.mark_absent"
		],
        "00 01 * * *": [
			"electra.custom.update_employee_salary"
		],
        "00 01 01 01 *": [
			"electra.custom.update_leave_policy"
		],
        "00 09 * * *": [
			"electra.custom.reservation_entrylist"
		],
        "0 0 1 * *": [
			"electra.custom.update_per_hour_cost"
		],
        
	},
	"daily": [
		"electra.alerts.update_lcm_due_status",
        "electra.custom.update_days_left",
        "electra.custom.reservation_entry",
		"electra.utils.update_project_projct_report_details_rq_job_enqueue"
        
		# "electra.custom.update_employee_salary"
	],
# 	"daily": [
# 		"electra.tasks.daily"
# 	],
	"hourly": [
		"electra.utils.reset_general_entry_purchase_rate",
        "electra.utils.reset_general_entry_purchase_rate",
	],
# 	"weekly": [
# 		"electra.tasks.weekly"
# 	]
	"monthly": [
		"electra.custom.isthimara_exp_mail",
        "electra.custom.update_per_hour_cost"
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
	"Employee Separation":"electra.overrides.CustomEmployeeSeparation",
    "Salary Slip":"electra.overrides.CustomSalarySlip",
}

jinja = {
	"methods": [
		"electra.utils.get_dns",
        # "electra.custom.unallocated_amount",
		"electra.utils.get_sos",
        "electra.utils.get_sos_so",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.receivable_report",
		"electra.electra.doctype.multi_project_day_plan.multi_project_day_plan.get_child_table_data",
		"electra.electra.doctype.multi_project_day_plan.multi_project_day_plan.get_driver_table_data",
		# "electra.custom.get_sales_person_invoice",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.get_sales_person",
		"electra.electra.doctype.report_dashboard.report_dashboard_print.get_accounts_ledger",
        "electra.custom.get_items",
        "electra.custom.get_pb_materials",
        "electra.custom.create_project_wo_print",
		"electra.custom.create_project_material_print",
		# "electra.utils.actual_vs_budgeted",
		"electra.electra.doctype.budgeted_vs_actual_report.budgeted_vs_actual_report.actual_vs_budgeted_test",
		"electra.electra.doctype.budgeted_vs_actual_test_report.budgeted_vs_actual_test_report.actual_vs_budgeted",
		"electra.utils.project_project_report",
		"electra.utils.work_order_brief_report",
		"electra.utils.work_order_detailed_report",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.ageing_report",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.ageing_report_test",
        "electra.utils.ageing_report_multicompany",
		"electra.custom.pay_consolidated_req",
		"electra.custom.return_total_amt1",
		"electra.electra.doctype.report_dashboard.report_dashboard_print.return_total_amt",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.return_total_amt_consolidate",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.return_account_total",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.return_account_summary_total",
        "electra.custom.scope_of_work",
        "electra.electra.doctype.cost_estimation.cost_estimation.get_data",
        "electra.utils.update_mat_total",
        "electra.utils.update_design_total",
        "electra.utils.update_work_total",
        "electra.utils.update_acc_total",
        "electra.utils.update_inst_total",
        "electra.utils.update_power_total",
        "electra.utils.update_tools_total",
        "electra.utils.update_other_total",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.statement_of_account",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.supplier_statement_of_account",
        "electra.electra.doctype.report_dashboard.report_dashboard_print.receipt_report",
        "electra.custom.less_previous_payment",
        "electra.custom.accounts_ledger_table",
		"electra.utils.get_timesheet",
		"electra.utils.get_timesheet_project",
		"electra.utils.project_details_report",
		"electra.utils.estimated_vs_actual",
		"electra.custom.amount_in_words_ar",
        "electra.custom.amount_in_words",
        "electra.custom.money_in_words",
        "electra.custom.get_data_for_pb",
		"electra.electra.doctype.report_dashboard.report_dashboard_print.statement_of_account_project",
		"electra.utils.project_profit_report_new",
        "electra.utils.project_profit_report_new1",
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

fixtures = ['Custom Field','Client Script','User Permission','Print Format']

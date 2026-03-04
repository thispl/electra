// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Salary Register Print"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_start(),
			"reqd": 1,
			on_change: function () {
				var from_date = frappe.query_report.get_filter_value('from_date')
				frappe.call({
					method: "electra.electra.report.monthly_salary_register_print.monthly_salary_register_print.get_to_date",
					args: {
						from_date: from_date
					},
					callback(r) {
						frappe.query_report.set_filter_value('to_date', r.message);
						frappe.query_report.refresh();
					}
				})
			},
			"width": "100px"
		},
		{
			"fieldname":"to_date",
			"label": __("To"),
			"fieldtype": "Date",
			"reqd": 1,
			on_change: function () {
				var from_date = frappe.query_report.get_filter_value('from_date')
				var to_date = frappe.query_report.get_filter_value('to_date')
				frappe.call({
					method: "electra.electra.report.monthly_salary_register_print.monthly_salary_register_print.get_diff_date",
					args: {
						from_date: from_date,
						to_date:to_date
					},
					callback(r) {
						frappe.query_report.set_filter_value('total_no_of_working_days', r.message);
						frappe.query_report.refresh();
					}
				})
			},
			"width": "100px"
		},
		{
			"fieldname":"grade",
			"fieldtype": "Link",
			"options": "Employee Grade",
			"label": __("Grade"),
		},
		{
			"fieldname": "currency",
			"fieldtype": "Link",
			"options": "Currency",
			"label": __("Currency"),
			"default": erpnext.get_currency(frappe.defaults.get_default("Company")),
			"width": "50px"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default": "Submitted",
			"width": "100px"
		},
		{
			"fieldname":"total_no_of_working_days",
			"label":__("Total No of Working Days"),
			"fieldtype":"Data",
			"width": "100px"
		}
	],

};


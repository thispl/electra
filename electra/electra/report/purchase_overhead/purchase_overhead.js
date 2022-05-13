// Copyright (c) 2016, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Purchase Overhead"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		



	],
	onload: function (report) {
        frappe.breadcrumbs.add("Invoice Status");
		var to_date = frappe.query_report.get_filter('to_date');
		to_date.refresh();
		to_date.set_input(frappe.datetime.month_end())

		var from_date = frappe.query_report.get_filter('from_date');
		from_date.refresh();
		from_date.set_input(frappe.datetime.month_start())
	}
};

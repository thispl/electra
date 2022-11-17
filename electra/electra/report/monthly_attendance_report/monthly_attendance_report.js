// Copyright (c) 2016, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Attendance Report"] = {
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
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			// "reqd": 1,
			// "default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
		},
	]
};

// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Wise Report"] = {
	"filters": [
		
		// {
		// 	"fieldname":"customer",
		// 	"label": __("Customer"),
		// 	"fieldtype": "Link",
		// 	"options": "Customer",
		// },
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd": 1
		},
		
		{
			"fieldname":"sales_person_user",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
			"default": frappe.defaults.get_user_default("Sales Person"),
			"width": "100px",
			"reqd": frappe.user.has_role("HOD") || frappe.user.has_role("Accounts User") || frappe.user.has_role("Accounts Manager")?0:1,
			// "reqd": 1
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1

		
		}
		


	]
};

// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Wise Target Report"] = {
	"filters": [
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Sales Person",
			"reqd": frappe.user.has_role("HOD") || frappe.user.has_role("Accounts User") || frappe.user.has_role("Accounts Manager")?0:1,
			"ignore_user_permissions":1
		},

		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"reqd":1,
			"options": [
				'January','February','March','April','May','June','July','August','September','October','November','December'
			],
		},

		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": [
				'','2023','2022','2021','2020','2019','2018','2017','2016','2015'
			],
		
		},

	]
};

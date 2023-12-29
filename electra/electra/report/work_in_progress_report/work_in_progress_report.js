// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Work in Progress Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			filters: {
				'has_project': 1
			},
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname":"project_no",
			"label": __("Project Number"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100px",
		},
		{
			"fieldname":"sales_order",
			"label": __("Sales Order No"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "100px",
		},
	]
};

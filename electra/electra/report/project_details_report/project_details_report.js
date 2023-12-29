// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Project Details Report"] = {
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
			"fieldname":"status",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["","Open", "propose Completion", "Completed","Cancelled"],
			// "default": "Open",
			"width": "100px"
		},
		
		{
			"fieldname":"project_no",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100px",
		},
		{
			"fieldname":"sales_order",
			"label": __("Order"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "100px",
		},
	]
};

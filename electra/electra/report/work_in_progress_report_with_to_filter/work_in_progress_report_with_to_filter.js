// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Work in Progress Report with To Filter"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"filters": {
				'has_project': 1
			},
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd":1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd":1
		},
		{
			"fieldname": "project",
			"label": __("Project Number"),
			"fieldtype": "Link",
			"options": "Project",
			"width": "100px",
			"get_query": function() {
				let company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				}
			}
		},
		{
			"fieldname": "sales_order",
			"label": __("Sales Order No"),
			"fieldtype": "Link",
			"options": "Sales Order",
			"width": "100px",
			"get_query": function() {
				let company = frappe.query_report.get_filter_value('company');
				return {
					filters: {
						'company': company
					}
				}
			}
		}
	]
};

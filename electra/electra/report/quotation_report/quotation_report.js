// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Quotation Report"] = {
	"filters": [
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
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px",
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px",
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["","Draft","Open","Replied","Partially Ordered","Ordered","Lost","Expired"],
			"width": "100px"
		},
		{
			"fieldname":"order_type",
			"label":__("Order Type"),
			"fieldtype":"Select",
			"options":["","Sales","Project"],
			"width": "100px"
		},
		{
			"fieldname":"valid_from_date",
			"label": __("Valid From Date"),
			"fieldtype": "Date",
			"width": "100px",
		},
		{
			"fieldname":"valid_to_date",
			"label": __("Valid To Date"),
			"fieldtype": "Date",
			"width": "100px",
		},
	]
};

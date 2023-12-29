// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "100px",
			"reqd":1,

			
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
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
			"fieldname":"invoice_type",
			"label": __("Invoice Type"),
			"fieldtype": "Select",
			"options": ["","Credit","Cash"],
			"width": "100px",
		},
		{
			"fieldname":"status",
			"label":__("Status"),
			"fieldtype":"Select",
			"options":["","Return","Credit Note Issued","Submitted","Paid","Partly Paid","Unpaid","Unpaid and Discounted","Partly Paid and Discounted","Overdue and Discounted","Overdue","Internal Transfer"],
			// "default": "Draft",
			"width": "100px"
		},

	]
};

// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Report Sales Order"] = {
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
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
		},
		{
			"fieldname":"lpo",
			"label": __("LPO Number"),
			"fieldtype": "Data",
		},
		{
			"fieldname":"sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person",
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["","Draft","On Hold","To Deliver and Bill","To Bill","To Deliver","Completed","Cancelled","Closed"],
			// "default": "Draft",
			"width": "100px"
		},
		{
			"fieldname":"order_type",
			"label":__("Order Type"),
			"fieldtype":"Select",
			"options":["","Sales","Project"],
			// "default": "Sales",
			"width": "100px"
		},
		
	]
};

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
			"default": frappe.datetime.year_start(),
			"reqd": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px",
			"default": frappe.datetime.year_end(),
			"reqd": 1
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
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
		// {
		// 	"fieldname":"valid_from_date",
		// 	"label": __("Valid From Date"),
		// 	"fieldtype": "Date",
		// 	"width": "100px",
		// },
		// {
		// 	"fieldname":"valid_to_date",
		// 	"label": __("Valid To Date"),
		// 	"fieldtype": "Date",
		// 	"width": "100px",
		// },
		// {
		// 	"fieldname":"amount_from",
		// 	"label": __("Amount From"),
		// 	"fieldtype": "Currency",
		// },
		// {
		// 	"fieldname":"amount_to",
		// 	"label": __("Amount To"),
		// 	"fieldtype": "Currency",
		// },
        {
            "fieldname": "amount_condition",
            "label": __("Select"),
            "fieldtype": "Select",
            "options": [">", "<", "=", "between"],
            "default": ">",
            "reqd": 1
        },
        {
            "fieldname": "amount_from",
            "label": __("Amount From"),
            "fieldtype": "Currency",
        },
        {
            "fieldname": "amount_to",
            "label": __("Amount To"),
            "fieldtype": "Currency",
            "depends_on": "eval: doc.amount_condition == 'between'",
        },
	]
};

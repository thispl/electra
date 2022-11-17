// Copyright (c) 2016, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Ledger Summary"] = {
	"filters": [

		{
			"fieldname":"item",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"default": frappe.defaults.get_default('Item')
		},

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},

		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		},


	]
};

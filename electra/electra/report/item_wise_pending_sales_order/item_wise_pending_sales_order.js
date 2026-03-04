// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Item Wise Pending Sales Order"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "options": "Item",
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
			"fieldname":"item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "100px",
			"reqd": 1
		},
		// {
		// 	"fieldname":"customer",
		// 	"label": __("Customer"),
		// 	"fieldtype": "Link",
		// 	"options": "Customer",
		// 	"width": "100px",
		// },
		// {
		// 	"fieldname":"sales_person",
		// 	"label": __("Sales Person"),
		// 	"fieldtype": "Link",
		// 	"options": "Sales Person",
		// 	"width": "100px",
		// 	// "reqd": 1
		// },

	]
};

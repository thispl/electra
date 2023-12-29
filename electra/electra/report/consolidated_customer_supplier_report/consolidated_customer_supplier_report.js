// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consolidated Customer Supplier Report"] = {
	"filters": [
		{
			"fieldname": "party_type",
			"label": __("Party Type"),
			"fieldtype": "Select",
			"options": ["","Supplier","Customer"],
			"width": "100px",
			"reqd":1,
			
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100px",
			"hidden": true,
			"depends_on": "eval: doc.party_type === 'Customer'"
			

		},
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": "100px",
			"hidden": true,
			"depends_on": "eval: doc.party_type === 'Supplier'"
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
	]
};

// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Summary Report"] = {
		"filters": [			 
			{
				"fieldname":"type",
				"label": __("Document"),
				"fieldtype": "Select",
				"reqd":1,
				"options": [
					" ",
					'Quotation','Sales Order','Sales Invoice'
				],
			},
		]
	};
	
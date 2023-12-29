// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Person Summary Report"] = {
	"filters": [
			{
				"fieldname":"type",
				"label": __("Document"),
				"fieldtype": "Select",
				"reqd":1,
				"options": [
					" ",'Quotation','Sales Order','Sales Invoice'
				],
				"default":" "
			},
			{
				"fieldname":"year",
				"label": __("Year"),
				"fieldtype": "Select",
				"reqd":1,
				"options": [
					' ','2020','2021','2022','2023','2024','2025','2026','2027','2028','2029','2030'
				],
			},
			{
				"fieldname":"order_type",
				"label": __("Type"),
				"fieldtype": "Select",
				"reqd":1,
				"options": [
					" ",'Monthly','Quarter','Half Yearly'
				],
				"default":" "
			},
			{
				"fieldname": "quarter",
				"label": __("Quarter"),
				"fieldtype": "Select",
				"width": "80",
				"options": ["", "Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4"],
				"hidden": true,
				"depends_on": "eval: doc.order_type === 'Quarter'"
			},
			{
				"fieldname": "half_yearly",
				"label": __("Half Yearly"),
				"fieldtype": "Select",
				"width": "80",
				"options": ["", "First Half", "Second Half"],
				"hidden": true,
				"depends_on": "eval: doc.order_type === 'Half Yearly'"
			}
		]
};
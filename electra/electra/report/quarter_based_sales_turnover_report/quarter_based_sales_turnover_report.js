// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Quarter Based Sales Turnover Report"] = {
	"filters": [
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Select",
			"reqd":1,
			"options": [
                '2020','2021','2022','2023','2024','2025','2026','2027'
            ],
		},
	
		{
			"fieldname": "quarter",
			"label": __("Quarter"),
			"fieldtype": "Select",
			"reqd":1,
			"width": "80",
			"options": ["Quarter 1","Quarter 2","Quarter 3","Quarter 4"]
		},

	]
};

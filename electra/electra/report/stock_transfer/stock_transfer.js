// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Transfer"] = {
	"filters": [
		{
			"fieldname": "source_company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company"
		},
		{
			"fieldname": "target_company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
		
		},

		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
		
		},

	]
};

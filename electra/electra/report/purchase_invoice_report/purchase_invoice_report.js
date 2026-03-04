// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Purchase Invoice Report"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"width": "200px",
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "200px",
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "200px",
		},
		{
			"fieldname":"group_by",
			"label": __("Group By"),
			"fieldtype": "Autocomplete",
			"options": ["Invoice", "Item"],
			// "default": "Invoice",
			"reqd": 1,
			"width": "200px",
		},
	]
};

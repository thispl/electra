// Copyright (c) 2016, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Ledger"] = {
	"filters": [

		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"default": frappe.defaults.get_default('Supplier')
		},

		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_default('Company')
		},

	]
};

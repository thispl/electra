// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Transfer Report"] = {
	"filters": [
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
		{
			"fieldname":"from_company",
			"label": __("From Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			"reqd":1,
			get_data: function(txt) {
				return frappe.db.get_link_options('Company');
			}
		},
		{
			"fieldname":"to_company",
			"label": __("To Company"),
			"fieldtype": "MultiSelectList",
			"options": "Company",
			// "reqd":1,
			get_data: function(txt) {
				return getCompanies();
			}
		},
		{
			"fieldname": "is_checked",
			"label": __("Is Checked"),
			"fieldtype": "Check",
			"default": 0, 
			"width": "100px",
			// "reqd":1,

		},
	]
};

function getCompanies() {
	return new Promise((resolve) => {
	frappe.call({
		method:"electra.custom.get_company",
		callback: function(r){
			if (r.message) {
				let options = r.message.map((c) => ({
					"value": c.name,
					"label": __(c.name),
					"description": ""
				}));
				resolve(options);

			}
		}
	})
})
}
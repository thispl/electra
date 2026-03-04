// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Material Transfer Report"] = {
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
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd":1,
		},
		{
			"fieldname":"source_company",
			"label": __("From Warehouse"),
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			"reqd":1,
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse',txt);
			}
		},
		{
			"fieldname":"to_warehouse",
			"label": __("To Warehouse"),
			"fieldtype": "MultiSelectList",
			"options": "Warehouse",
			// "reqd":1,
			get_data: function(txt) {
				return frappe.db.get_link_options('Warehouse',txt);
			}
		},
	]
};

function getCompanies() {
	return new Promise((resolve) => {
	frappe.call({
		method:"electra.custom.get_company",
		callback: function(r){
			if (r.message) {
				console.log(r.message)
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
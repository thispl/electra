// Copyright (c) 2016, TeamPRO and contributors
// For license information, please see license.txt
/* eslint-disable */
frappe.require("assets/erpnext/js/financial_statements.js", function () {
	frappe.query_reports["Monitoring Panel"] = {
		"filters": [
			{
				"fieldname": "from_date",
				"label": __("From Date"),
				"fieldtype": "Date",
				"width": "80",
				"reqd": 1,
				// "hidden": 1,
				"default": frappe.datetime.add_months(frappe.datetime.get_today(), -240),
			},
			{
				"fieldname": "to_date",
				"label": __("To Date"),
				"fieldtype": "Date",
				"width": "80",
				"reqd": 1,
				// "hidden": 1,
				"default": frappe.datetime.get_today()
			},
			{
				"fieldname": "company",
				"label": __("Company"),
				"fieldtype": "Link",
				"width": "80",
				// "reqd": 1,
				"options": "Company",

			},
			{
				"fieldname": "item_group",
				"label": __("Category"),
				"fieldtype": "Link",
				"width": "80",
				"options": "Item Group"
			},
			{
				"fieldname": "item_code",
				"label": __("Item"),
				"fieldtype": "Link",
				"width": "80",
				"options": "Item",
				"get_query": function () {
					return {
						query: "erpnext.controllers.queries.item_query",
					};
				}
			},
			{
				"fieldname": "warehouse",
				"label": __("Warehouse"),
				"fieldtype": "MultiSelectList",
				"width": "80",
				get_data: function (txt) {
					company = frappe.query_report.get_filter_value('company');
					country = frappe.query_report.get_filter_value('country');
					if (company && country) {
						return frappe.db.get_link_options('Warehouse', txt, { 'country': country, 'company': company })
					}
					if (company) {
						return frappe.db.get_link_options('Warehouse', txt, { 'company': company })
					}
					if (country) {
						return frappe.db.get_link_options('Warehouse', txt, { 'country': country })
					}
					return frappe.db.get_link_options('Warehouse', txt)
				},
			},
			{
				"fieldname": "currency",
				"label": __("Currency"),
				"fieldtype": "Link",
				"width": "80",
				"options": "Currency"
			},
			{
				"fieldname": 'show_stock_ageing_data',
				"label": __('Show Stock Ageing Data'),
				"fieldtype": 'Check'
			},
		],
		"formatter": function (value, row, column, data, default_formatter) {
			value = default_formatter(value, row, column, data);
			$.each(row,function(i,d){
				if(d.colIndex == 0){
					d.html = 10
					console.log(d.html)
				}
				
			});
			if (data["status"] === 'Low Quantity') {
				if (column['fieldname'] == 'status') {
					value = "<span style='color:red!important;font-weight:bold'>" + value + "</span>";
				}

			}
			if (data["status"] === 'Ideal Quantity') {
				if (column['fieldname'] == 'status') {
					value = "<span style='color:green!important;font-weight:bold'>" + value + "</span>";
				}

			}
			if (data["status"] === 'Frozen Item') {
				if (column['fieldname'] == 'status') {
					value = "<span style='color:blue!important;font-weight:bold'>" + value + "</span>";
				}
			}
			return value;
		},
		onload: function (frm) {
			frappe.breadcrumbs.add('Senergy');
		}
	}

});
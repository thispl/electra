// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Itemwise Previous Sales Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname": "document",
			"label": __("Document"),
			"fieldtype": "Select",
			"options": ["", "Quotation", "Sales Order", "Sales Invoice", "Delivery Note"],
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1
		},
		{
			"fieldname": "item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname": "amount",
			"label": __("Amount"),
			"fieldtype": "Select",
			"options": ["", "Between", "Greater than", "Less than"]
		},
		{
			"fieldname": "amount_from",
			"label": __("Amount From"),
			"fieldtype": "Currency",
			"depends_on": "eval:doc.amount == 'Between' || doc.amount == 'Greater than'",
		},
		{
			"fieldname": "amount_to",
			"label": __("Amount To"),
			"fieldtype": "Currency",
			"depends_on": "eval:doc.amount == 'Between' || doc.amount == 'Less than'",
		}
	]
};

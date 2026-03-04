// Copyright (c) 2026, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Sales Register - Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"customer_group",
			"label": __("Customer Group"),
			"fieldtype": "Link",
			"options": "Customer Group"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd":1
		},
		
		{
			"fieldname":"sales_person_user",
			"label": __("Sales Person User"),
			"fieldtype": "Link",
			"options": "Sales Person"
		},
		{
			"fieldname":"item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group"
		},
		
		{
			"fieldname": "summarise_based_on",
			"label": __("Summarise Based On"),
			"fieldtype": "Select",
			"options": ['','Item Group'],
		}
	]
};

erpnext.utils.add_dimensions('Sales Register', 7);

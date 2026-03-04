// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Trip Sheet"] = {
	"filters": [
	   // {
	   // 	"fieldname":"customer",
	   // 	"label":__("Customer"),
	   // 	"fieldtype":"Link",
	   // 	"options":"Customer",
	   // 	"default": frappe.defaults.get_user_default("Customer"),
	   // 	"width": "200px",
	   // 	"reqd": 1
	   // },
	   {
		   "fieldname":"vehicle_number",
		   "label":__("Vehicle Number"),
		   "fieldtype":"Link",
		   "options":"Vehicle",
		   "width": "200px",
		   

	   }

   ]
};

// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Plant and Equipment"] = {
    "filters": [
		{
            "fieldname": "plant",
            "label": __("Plant"),
            "fieldtype": "Data",
            "width": "200px"
        },
        {
            "fieldname": "equipment",
            "label": __("Equipment"),
            "fieldtype": "Data",
            "width": "200px"
        },
		{
            "fieldname": "make",
            "label": __("Make"),
            "fieldtype": "Data",
            "width": "200px"
        },
		{
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Data",
            "width": "200px"
        },
    ]
};

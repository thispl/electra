// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Custom Profit and Loss Statement"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        }
    ],
    "onload": function(report) {
        // Set the title of the report
        var title = __("Profit and Loss Statement") + " (" + report.filters.from_date + " to " + report.filters.to_date + ")";
        $(".page-title h1").html(title);
    }
};


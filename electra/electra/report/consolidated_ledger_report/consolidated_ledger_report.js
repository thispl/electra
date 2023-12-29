// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consolidated Ledger Report"] = {
	"filters": [
		{
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"reqd":1,
			"get_query": function () {
				return {
					filters: {
						"company": "Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)"
					}
				};
			},
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd":1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "100px",
			"reqd":1,
		},

	],
	onload: function(report) {
		const views_menu = report.page.add_custom_button_group(__('Print'));

		report.page.add_custom_menu_item(views_menu, __("Consolidated Ledger Report"), function() {
			var filters = report.get_values();
			frappe.route_options = {
				"account": filters.account,
			}
			window.open(
				frappe.urllib.get_full_url("/app/report-dashboard/?account="+encodeURIComponent("Ledger Summary Report" +':'+ filters.account +':'+ filters.from_date +':'+ filters.to_date)));
			// frappe.set_route('report-dashboard', 'Report Dashboard', {account: filters.account});
			// var print_format ="Ledger Summary Report";
			// var f_name = filters.account
			// window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
			// 	+ "doctype=" + encodeURIComponent("Report Dashboard")
			// 	+ "&name=" + encodeURIComponent(f_name)
			// 	+ "&trigger_print=1"
			// 	+ "&format=" + print_format
			// 	+ "&no_letterhead=0"
			// ));
		});

	}
};

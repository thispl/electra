// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Stock In Hand WIP"] = {
	"filters": [
		{
			"fieldname": "project_budget",
			"label": __("Project Budget"),
			"fieldtype": "Link",
			"options": "Project Budget",
			"filters": {
				'docstatus': 1
			},
		},
		{
			"fieldname": "consolidate_invoices",
			"label": __("Consolidate Invoices"),
			"fieldtype": "Check",
		},
	],
	// onload: function(report) {
	// 	report.page.add_inner_button(__("Issue Stock"), function () {
	// 		const project_budget = frappe.query_report.get_filter_value('project_budget') || "ENG-PB-2025-00076-9";

	// 		frappe.call({
	// 			method: "electra.electra.report.stock_in_hand_wip.stock_in_hand_wip.process_stock_issue",
	// 			// args: {
	// 			// 	"project_budget": project_budget,
	// 			// },
	// 			freeze: true,
	// 			freeze_message: "Please wait ...",
	// 			callback: function(r) {
					
	// 			},
	// 		});
	// 	});
	// },
};

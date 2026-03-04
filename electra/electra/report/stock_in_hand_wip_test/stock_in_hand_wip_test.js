// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.query_reports["Stock In Hand WIP Test"] = {
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
		
		// {
		// 	"fieldname": "consolidate_invoices",
		// 	"label": __("Consolidate Invoices"),
		// 	"fieldtype": "Check",
		// 	// "on_change": function() {
		// 	// 	toggle_issue_stock_button(frappe.query_report);
		// 	// }
		// },
	],
	onload: function(report) {
		toggle_issue_stock_button(frappe.query_report);
	},
};

function toggle_issue_stock_button(report) {
	report.page.clear_inner_toolbar();

	if (!frappe.query_report.get_filter_value('consolidate_invoices')) {
			report.page.add_inner_button(__("Issue Stock"), function () {
			const project_budget = frappe.query_report.get_filter_value('project_budget') || '';

			frappe.call({
				method: "electra.electra.report.stock_in_hand_wip_test.stock_in_hand_wip_test.process_stock_issue",
				args: {
					"project_budget": project_budget,
				},
				freeze: true,
				freeze_message: "Please wait ...",
				callback: function(r) {
					
				},
			});
		});
		}
}

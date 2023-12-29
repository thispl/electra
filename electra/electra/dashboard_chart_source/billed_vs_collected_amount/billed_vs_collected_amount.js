frappe.provide("frappe.dashboards.chart_sources");
frappe.dashboards.chart_sources["Billed vs Collected Amount"] = {
    method: "electra.electra.dashboard_chart_source.billed_vs_collected_amount.billed_vs_collected_amount.get_data",
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        },
    ]
};
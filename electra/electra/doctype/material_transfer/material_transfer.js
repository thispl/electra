// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Material Transfer', {
	refresh: function(frm) {
		if (frm.doc.docstatus > 0) {
			// frm.show_stock_ledger();
			frm.add_custom_button(__("Stock Ledger"), function () {
				frappe.db.get_value('Stock Entry',{stock_entry_type: "Material Transfer",material_transfer: frm.doc.name},'name',
					(r) => {
						if (r && r.name) {
							frappe.route_options = {
								reference_no: frm.doc.name,
								from_date: frm.doc.requested_date,
								to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
								company: frm.doc.company,
								voucher_no: r.name,
								show_cancelled_entries: frm.doc.docstatus === 2,
								ignore_prepared_report: true
							};
							frappe.set_route("query-report", "Stock Ledger Report - Project");
						} else {
							frappe.throw("No Stock Entry found for Material Transfer:", frm.doc.name);
						}
					}
				);
			}, __("View"));
			
		}
	}
});

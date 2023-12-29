// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('General Settings', {
	// refresh: function(frm) {

	// }
	setup(frm){
		frm.get_docfield('company_series').allow_bulk_edit = 1
	}
});

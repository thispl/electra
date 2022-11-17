// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Internal Payment Request', {
	// refresh: function(frm) {

	// }
	onload(frm) {
		frm.set_query('purchase_invoice',"table_7", function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				filters: [
					['Purchase Invoice','supplier','=',d.document_type]
			]
			};
		});
		
	},
});
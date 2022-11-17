// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Confirmation', {
	// refresh: function(frm) {

	// }
	refresh(frm){
		frm.trigger('print')
	},
	onload(frm){
		if(frm.doc.docstatus != 1){
		frm.trigger('print')
		frm.set_value('confirmed_by',frappe.session.user)
		}
		frappe.db.get_value('Stock Transfer', {'name':frm.doc.ic_material_transfer_confirmation}, ["transferred_date"], function(value) {
			console.log(value)
			frm.set_value("transferred_date",value.transferred_date);
		});
	},
	
	print: function (frm) {
		frm.add_custom_button(__("Print"), function () {
			if (frm.doc.parent_company) {
				var letter_head = frm.doc.parent_company
			}
			else {
				var letter_head = frm.doc.company
			}
			var f_name = frm.doc.name
			var print_format = "Stock Confirmation Test";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Stock Confirmation")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
				+ "&letterhead=" + encodeURIComponent(letter_head)
			));


		});
	},
});

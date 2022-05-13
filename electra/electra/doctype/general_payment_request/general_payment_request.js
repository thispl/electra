// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('General Payment Request', {
	onload: function(frm) {
		if(frm.doc.__islocal){
			frm.set_value('transaction_date',frappe.datetime.nowdate())
		}
	},
	setup: function(frm) {
		
		
		frm.set_query("party_type", function() {
			return {
				query: "erpnext.setup.doctype.party_type.party_type.get_party_type",
			};
		});
	}
});

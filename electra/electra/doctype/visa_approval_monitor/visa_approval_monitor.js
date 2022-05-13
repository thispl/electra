// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Visa Approval Monitor', {
	// refresh: function(frm) {

	// }
	onload:function(frm){
		frm.trigger("balance")

},
	balance:function(frm){
		var used_visa=frm.doc.used_visa
		var allocated=frm.doc.allocated_numbers
		var bal=allocated-used_visa
		console.log(bal)
		if (frm.doc.used_visa&&frm.doc.allocated_numbers){
		frm.set_value("balance",bal)
		}
	}	
});

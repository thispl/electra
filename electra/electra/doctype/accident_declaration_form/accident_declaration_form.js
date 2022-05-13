// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accident Declaration Form', {
	// refresh: function(frm) {

	// }
	date(frm){
		if(frm.doc.date){
			frm.call('get_day')
			.then(r=>{
				frm.set_value('day',r.message)
			})
		}
	}
});

// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Availability Report', {
	// refresh: function(frm) {

	// }
	item_code(frm){
		frm.call('get_data').then(r=>{
			if (r.message) {
				frm.fields_dict.html.$wrapper.empty().append(r.message)
			}
		})		
	}
});

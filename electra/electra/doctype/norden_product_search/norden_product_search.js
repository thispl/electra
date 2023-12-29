// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Norden Product Search', {
	refresh: function(frm) {
		frm.disable_save()

		frm.set_query('item',{
			filters:{
				'brand':"NORDEN"
			}
		})
	},
	item(frm){
		frappe.call({
			method:"electra.utils.get_norden_item",
			args:{
				item:frm.doc.item,
			},
			callback(r){
				$.each(r.message,function(i,d){
					frm.fields_dict.html.$wrapper.empty().append(d)
				})
			}
		})
	},
});


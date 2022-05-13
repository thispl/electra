// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('CE Item Page', {
	refresh: function(frm) {
		frm.disable_save()
	},
	// msow(frm){
	// 	if (msow){
	// 		frm.add_child('design',{
	// 			'msow': frm.doc.msow
	// 		})
	// 		frm.refresh_field('design')
	// }
	// },
	submit(frm){
			frm.call('copy_ce_items')
			.then(r=>{
				if(r.message == 'ok'){
					frappe.set_route("Form", "Cost Estimation", frm.doc.cost_estimation);
					cur_frm.reload_doc()
				}
				
			})
		}
});
frappe.ui.form.on('CE Items', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
	},
})
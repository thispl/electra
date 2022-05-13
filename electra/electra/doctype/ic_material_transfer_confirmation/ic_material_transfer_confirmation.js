// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('IC Material Transfer Confirmation', {
	validate: function(frm) {
		$.each(frm.doc.items,function(i,d){
			d.t_warehouse = frm.doc.default_target_warehouse
		})
		frm.refresh_field("items")
	},
	target_company(frm){
		frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company':frm.doc.target_company}, ["name"], function(value) {
			console.log(value)
			frm.set_value("default_target_warehouse",value.name);
		});
	},
});

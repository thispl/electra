// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Transfer', {
	refresh(frm){
		frm.trigger('print')
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
	},
	onload(frm){
		if(frm.doc.docstatus != 1 ){
			if(frm.doc.is_local){
				frm.trigger('print')
				frm.set_value('transferred_by',frappe.session.user)
				frm.set_value('transferred_date',frappe.datetime.nowdate())
				}
		}
	},
	set_series(frm) {
		frappe.call({
			method: "electra.utils.get_series",
			args: {
				company: frm.doc.company,
				doctype: frm.doc.doctype
			},
			callback: function (r) {
				if (r) {
					frm.set_value('naming_series', r.message)
				}
			}
		});
	},
	
	after_save(frm){
		if(frm.doc.workflow_state == 'Rejected'){
		let d = new frappe.ui.Dialog({
		   title: 'Cancellation Remark',
		   fields: [
			   {
				   label: 'Reason',
				   fieldname: 'reason',
				   fieldtype: 'Small Text'
			   },
			  ],
		   primary_action_label: 'Submit',
		   primary_action(values) {
			   console.log(values.reason);
			   d.hide();
			   frm.set_value('cancellation_remark',values.reason);
		   }
	   
	   });
	   d.show();
	frappe.msgprint("please fill the cancellation remarks")
		}
   },
	validate: function(frm) {
		frm.set_value('transferred_by',frappe.session.user)
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

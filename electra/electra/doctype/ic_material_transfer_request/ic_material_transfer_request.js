// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('IC Material Transfer Request', {
	validate: function(frm) {
		$.each(frm.doc.items,function(i,d){
		frappe.db.get_value('Warehouse', {'default_for_stock_transfer':1,'company':frm.doc.company}, ["name"], function(value) {
			d.t_warehouse = value.name
		});
		})
		$.each(frm.doc.items,function(i,d){
			frappe.call({
				method: 'electra.custom.get_stock_balance_from_wh',
				args:{
					'item_code': d.item_code,
					'warehouse': frm.doc.default_source_warehouse
				},
				callback(r){
				   if (r.message){ 
						if (r.message.actual_qty < d.qty){
							frappe.msgprint("Expected Item Quantity not available in "+ frm.doc.default_source_warehouse +" for "+d.item_code)
							frappe.validated = false
						}
					   }
					}
					})
			d.s_warehouse = frm.doc.default_source_warehouse
		})
		frm.refresh_field("items")
	},
	onload:function(frm){
		frm.get_field("items_html").$wrapper.html();
		if(frm.doc.__islocal){
			frm.set_value("requested_date",frappe.datetime.nowdate())
			frm.set_value("raised_by",frappe.session.user)
			frm.set_df_property("sales_order","hidden",1)	
	}
	},
	set_so(frm){
		if(frm.doc.source_company){
			frm.set_df_property("sales_order","hidden",0)
		}
	},
	sales_order(frm){
		frappe.call({
			"method" : "frappe.client.get",
			args:{
				doctype: 'Sales Order',
				filters: {
					"name": frm.doc.sales_order
				},
				fields: ['items']
			},
			callback:function(r){
				$.each(r.message.items,function(i,d){
					var row = frappe.model.add_child(frm.doc, "Material Transfer Items", "items");
					frappe.call({
						method: 'electra.electra.doctype.material_transfer_inter_company.material_transfer_inter_company.get_item_availability',
						args:{
							'item_code':d.item_code,
							'source_warehouse' : frm.doc.default_source_warehouse
						},
						callback(r){
							row.availability = r.message.actual_qty
						}
					})
					
					row.s_warehouse = frm.doc.default_source_warehouse;
					row.t_warehouse = frm.doc.default_target_warehouse;
					row.item_code = d.item_code;
					row.uom = d.uom;
					row.qty = d.qty;
					row.project = d.project;
				})
				refresh_field("items")
			}
		})
	},
	

	source_company(frm){
		frm.trigger("set_so")
		frappe.call({
			"method" : "electra.electra.doctype.material_transfer_inter_company.material_transfer_inter_company.get_material_transfer_warehouse",
			args:{
				"company": frm.doc.source_company
			},
			callback:function(r){
				if(r.message){
					frm.set_value("default_source_warehouse",r.message);
				}
				
			}
		})
	},
	setup: function(frm) {
		frm.set_query("sales_order", function() {
			return {
				"filters": {
					"company": ["in",[frm.doc.source_company,frm.doc.target_company]],
				}
			}
		});
		frm.set_query("s_warehouse", "items", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Warehouse', 'company', '=', frm.doc.source_company]
				]
			};
		});

	}
});



frappe.ui.form.on('Material Transfer Items', {
	items_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.s_warehouse = frm.doc.default_source_warehouse;
		frm.refresh_field("items");
	},
	item_code(frm,cdt,cdn) {
	    var child = locals[cdt][cdn]
		frappe.call({
	        method: 'electra.custom.stock_popup',
	        args:{
	            'item_code': child.item_code
	        },
	        callback(d){
	           if (d.message){ 
				frm.get_field("items_html").$wrapper.html(d.message);
        	           }
        	       }
        	    })
		
}
});


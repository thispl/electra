// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Transfer', {
	refresh(frm){
		var input = 'input[data-fieldname="item_code"][data-doctype="Material Transfer Items"]';
		var isFocus = false;
		frm.fields_dict.items.grid.wrapper.on('click', input, function (e) {
			if (!isFocus) {
				const item_code = e.currentTarget.value;
				frappe.call({
					method: 'electra.custom.stock_popup',
					args: {
						'item_code': item_code,
						'company':frm.doc.source_company
					},
					callback(d) {
					    console.log(d.message)
						if (d.message) {
							frm.get_field("items_html").$wrapper.html(d.message);
						}
					}
				})
			}
			isFocus = false;
		});
		frm.add_custom_button(__("Temp SC"), function () {
			frm.call('on_submit')
			.then(r=>{
				console.log('done')
			})


		})
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
	print: function (frm) {
		
		frm.add_custom_button(__("Print"), function () {
			if (frm.doc.parent_company) {
				var letter_head = frm.doc.parent_company
			}
			else {
				var letter_head = frm.doc.company
			}
			var f_name = frm.doc.name
			var print_format = "Stock Transfer Test";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Stock Transfer")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
				+ "&letterhead=" + encodeURIComponent(letter_head)
			));


		});
	},
	source_company(frm){
	    if (frm.doc.source_company == "MARAZEEM SECURITY SERVICES" || frm.doc.source_company == "MARAZEEM SECURITY SERVICES - SHOWROOM" || frm.doc.source_company == "MARAZEEM SECURITY SERVICES - HO") {
			frm.set_value('letter_head', "MARAZEEM SECURITY SERVICES")
		}
		if (frm.doc.source_company == "KINGFISHER TRADING AND CONTRACTING COMPANY" || frm.doc.source_company == "KINGFISHER - TRANSPORTATION" || frm.doc.source_company == "KINGFISHER - SHOWROOM") {
			frm.set_value('letter_head', "KINGFISHER TRADING AND CONTRACTING COMPANY")
		}
		if (frm.doc.source_company == "Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)" || frm.doc.source_company == "ELECTRA - ALKHOR SHOWROOM" || frm.doc.source_company == "ELECTRA - BARWA SHOWROOM" || frm.doc.source_company == "ELECTRA - BINOMRAN SHOWROOM" || frm.doc.source_company == "ELECTRA  - NAJMA SHOWROOM" || frm.doc.source_company == "ELECTRICAL DIVISION - ELECTRA" || frm.doc.source_company == "MEP DIVISION - ELECTRA" || frm.doc.source_company == "STEEL DIVISION - ELECTRA" || frm.doc.source_company == "TRADING DIVISION - ELECTRA" || frm.doc.source_company == "INTERIOR DIVISION - ELECTRA" || frm.doc.source_company == "ENGINEERING DIVISION - ELECTRA") {
			frm.set_value('letter_head', "Electra")
	}
	},
	// before_submit(frm){
	// 	frm.set_value('transferred_by',frappe.session.user)
	// },
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
	    
	    $.each(frm.doc.items,function(i,j){
	        if(j.item_group == "OptiNor"){
	            j.uom = "Meter"
	        }
	    })
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
frappe.ui.form.on('Material Transfer Items', {
	item_code(frm,cdt,cdn) {
	    var child = locals[cdt][cdn]
		frappe.call({
	        method: 'electra.custom.stock_popup',
	        args:{
	            'item_code': child.item_code,
				'company':frm.doc.source_company
	        },
	        callback(d){
	           if (d.message){ 
				frm.get_field("items_html").$wrapper.html(d.message);
        	           }
        	       }
        	    })
		
}
});
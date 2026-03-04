// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Request', {
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
						if (d.message) {
							frm.get_field("items_html").$wrapper.html(d.message);
						}
					}
				})
			}
			isFocus = false;
		});
		frm.trigger('print')
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
		frm.set_query("sales_invoice", function() {
			return {
				"filters": {
					"company": frm.doc.company,
				}
			};
		});
		
	// 	frm.add_custom_button(__("Get Items from Product Bundle"), function () {
	// 		let d = new frappe.ui.Dialog({
	// 			size: "small-large",
	// 			title: 'Fetch Items from Product Bundle',
	// 			fields: [
	// 				{
	// 					label: 'Product Bundle',
	// 					fieldname: 'bundle',
	// 					fieldtype: 'Link',
	// 					options: "Product Bundle",
	// 					reqd: 1
	// 				},
	// 				{
	// 					label: 'Proceed',
	// 					fieldname: 'proceed',
	// 					fieldtype: 'Button'
	// 				},
	// 			],
	// 		});
		
	// 		d.get_input("proceed").on("click", function () {
	// 			let bundle = d.get_value("bundle");
	// 			if (!bundle) {
	// 				frappe.msgprint(__('Please select a Product Bundle.'));
	// 				return;
	// 			}
		
	// 			d.hide();
	// 			frappe.call({
	// 				method: "electra.custom.product_bundle_items",
	// 				args: {
	// 					"bundle": bundle,
	// 				},
	// 				callback: function(r) {
	// 					if (r.message) {
	// 						console.log("Product Bundle Items:", r.message); // Debug log
	// 						r.message.forEach(item => {
	// 							frm.add_child('items', {
	// 								"item_code": item.item_code,
	// 								"qty": item.qty,
	// 								"uom": item.uom,
	// 								"item_name": item.description
	// 							});
	// 						});
	// 						frm.refresh_field("items");
	// 					} else {
	// 						frappe.msgprint(__('No items found for the selected Product Bundle.'));
	// 					}
	// 				},
	// 				error: function(error) {
	// 					frappe.msgprint(__('Error fetching Product Bundle items.'));
	// 					console.error("Error fetching Product Bundle items:", error); // Log any error
	// 				}
	// 			});
	// 		});
		
	// 		d.show(); 
	// 	});
		
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
	onload:function(frm){
		frm.trigger('print')
		frm.get_field("items_html").$wrapper.html();
		if(frm.doc.__islocal){
			frm.set_value("requested_date",frappe.datetime.nowdate())
			frm.set_value("raised_by",frappe.session.user)
			// frm.set_df_property("sales_order","hidden",1)	
	}
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
			var print_format = "Stock Request Test";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Stock Request")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
				+ "&letterhead=" + encodeURIComponent(letter_head)
			));


		});
	},
	validate: function(frm) {
		
		frm.trigger("source_company")
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
						if (r.message[0].qty < d.qty){
							console.log(r.message[0])
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
	
	set_so(frm){
		if(frm.doc.source_company){
			frm.set_df_property("sales_order","hidden",0)
		}
	},
	sales_order(frm){
		frappe.call({
			method : "electra.electra.doctype.stock_request.stock_request.so_order_type",
			args:{
				so: frm.doc.sales_order,
			},
			callback:function(response){
				frm.clear_table("items");
				if (response.message == 'Sales') {
					frappe.call({
						method: "electra.custom.sales_order_items_with_bundle",
						args: {
							sales_order_name: frm.doc.sales_order,
						},
						freeze: true,
						freeze_message:'Fetching Items',
						callback: function (r) {
							if (r.message) {
								$.each(r.message, function (i, item) {
									frm.add_child("items", {
										item_code: item.item_code,
										item_name: item.item_name,
										uom: item.uom,
										qty: item.qty,
									});
								});
			
								frm.refresh_field("items");
							}
						},
						
					});
				}
				else {
					frappe.call({
						"method" : "frappe.client.get",
						args:{
							doctype: 'Sales Order',
							filters: {
								"name": frm.doc.sales_order
							},
							fields: ['*']
						},
						freeze:true,
						freeze_message:(__('Fetching Items')),
						callback:function(r){
							frm.clear_table('items')
								$.each(r.message.materials, function(i, d) {
									frm.add_child('items', {
										"item_code": d.item,
										"item_name": d.item_name,
										"qty": d.qty,
										"uom": d.unit,
										"project": frm.doc.project,
										"docname": d.docname,
										"msow": d.msow,
									});
								});
								refresh_field("items")
							}
					})
				}
				refresh_field("items")
			}
		});
		frm.clear_table("items")
		
	},
	// sales_order(frm){
	// 	frm.clear_table("items")
	// 	frappe.call({
	// 		"method" : "frappe.client.get",
	// 		args:{
	// 			doctype: 'Sales Order',
	// 			filters: {
	// 				"name": frm.doc.sales_order
	// 			},
	// 			fields: ['*']
	// 		},
	// 		freeze:true,
	// 		freeze_message:(__('Fetching Items')),
	// 		callback:function(r){
	// 			frm.clear_table('items')
	// 			if(r.message.order_type == 'Sales'){
	// 				$.each(r.message.items,function(i,d){
	// 					var row = frappe.model.add_child(frm.doc, "Material Transfer Items", "items");
	// 					if (frm.doc.default_source_warehouse){
	// 						frappe.call({
	// 							method: 'electra.electra.doctype.material_transfer_inter_company.material_transfer_inter_company.get_item_availability',
	// 							args:{
	// 								'item_code':d.item_code,
	// 								'source_warehouse' : frm.doc.default_source_warehouse
	// 							},
	// 							callback(r){
	// 								row.availability = r.message.actual_qty;
	// 							}
	// 						})
	// 					}
	// 					row.s_warehouse = frm.doc.default_source_warehouse;
	// 					row.t_warehouse = frm.doc.default_target_warehouse;
	// 					row.item_code = d.item_code;
	// 					row.item_name = d.item_name;
	// 					row.project = r.message.project;
	// 					row.uom = d.uom;
	// 					var mr_qty=d.qty-d.custom_sr_qty;
	// 					row.qty=mr_qty;
	// 					// row.qty = d.qty;
	// 					row.custom_row_id = d.custom_row_id;
	// 				})
	// 				refresh_field("items")
	// 			}
	// 			else{
	// 				$.each(r.message.materials, function(i, d) {
	// 					frm.add_child('items', {
	// 						"item_code": d.item,
	// 						"item_name": d.item_name,
	// 						"qty": d.qty,
	// 						"uom": d.unit,
	// 						"project": frm.doc.project
	// 					});
	// 				});
	// 				refresh_field("items")
	// 			}
				
				
	// 		}
	// 	})
	// },
	sales_invoice(frm){
		frm.clear_table("items")
		frappe.call({
			"method" : "frappe.client.get",
			args:{
				doctype: 'Sales Invoice',
				filters: {
					"name": frm.doc.sales_invoice
				},
				fields: ['*']
			},
			freeze:true,
			freeze_message:(__('Fetching Items')),
			callback:function(r){
				frm.clear_table('items')
				if(r.message.order_type == 'Sales'){
					$.each(r.message.items,function(i,d){
						var row = frappe.model.add_child(frm.doc, "Material Transfer Items", "items");
						if (frm.doc.default_source_warehouse){
							frappe.call({
								method: 'electra.electra.doctype.material_transfer_inter_company.material_transfer_inter_company.get_item_availability',
								args:{
									'item_code':d.item_code,
									'source_warehouse' : frm.doc.default_source_warehouse
								},
								callback(r){
									row.availability = r.message.actual_qty;
								}
							})
						}
						row.s_warehouse = frm.doc.default_source_warehouse;
						row.t_warehouse = frm.doc.default_target_warehouse;
						row.item_code = d.item_code;
						row.item_name = d.item_name;
						row.project = r.message.project;
						row.uom = d.uom;
						row.qty = d.qty;
						row.custom_row_id = d.custom_row_id;
					})
					refresh_field("items")
				}
				else{
					$.each(r.message.materials, function(i, d) {
						frm.add_child('items', {
							"item_code": d.item,
							"item_name": d.item_name,
							"qty": d.qty,
							"uom": d.unit,
							"project": frm.doc.project
						});
					});
					refresh_field("items")
				}
				
				
			}
		})
	},
	
	company(frm){
		frm.set_query("default_source_warehouse",function() {
			return {
				filters: [
					['Warehouse', 'company', '=', frm.doc.source_company]
				]
			};
		});
		frm.trigger("set_series")
	    if (frm.doc.company == "MARAZEEM SECURITY SERVICES" || frm.doc.company == "MARAZEEM SECURITY SERVICES - SHOWROOM" || frm.doc.company == "MARAZEEM SECURITY SERVICES - HO") {
			frm.set_value('letter_head', "Marazeem with Footer Text")
		}
		if (frm.doc.company == "KINGFISHER TRADING AND CONTRACTING COMPANY" || frm.doc.company == "KINGFISHER - TRANSPORTATION" || frm.doc.company == "KINGFISHER - SHOWROOM") {
			frm.set_value('letter_head', "KINGFISHER TRADING AND CONTRACTING COMPANY")
		}
		if (frm.doc.company == "Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)" || frm.doc.company == "ELECTRA - BARWA SHOWROOM" || frm.doc.company == "ELECTRA - ALKHOR SHOWROOM" || frm.doc.company == "ELECTRA - BINOMRAN SHOWROOM" || frm.doc.company == "ELECTRA  - NAJMA SHOWROOM" || frm.doc.company == "ELECTRICAL DIVISION - ELECTRA" || frm.doc.company == "MEP DIVISION - ELECTRA" || frm.doc.company == "STEEL DIVISION - ELECTRA" || frm.doc.company == "TRADING DIVISION - ELECTRA" || frm.doc.company == "INTERIOR DIVISION - ELECTRA" || frm.doc.company == "ENGINEERING DIVISION - ELECTRA") {
			frm.set_value('letter_head', "Electra")
	}
	},
	default_source_warehouse(frm){
		$.each(frm.doc.items,function(i,d){
			d.s_warehouse = frm.doc.default_source_warehouse
		})
	},
	source_company(frm){
		frm.trigger("set_so")
		if(!frm.doc.default_source_warehouse){
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
		}
		
	},
	setup: function(frm) {
		frm.set_query("sales_order", function() {
			return {
				// "filters": {
				// 	"company": ["in",[frm.doc.source_company,frm.doc.target_company]],
				// }
				"filters": {
					"company": frm.doc.company,
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


frappe.ui.form.on('Quotation', {
    converted_by(frm){
        frappe.call({
            method: "electra.utils.get_user_details",
            args:{
                "user": frm.doc.converted_by
            },
            callback:function(d){
                console.log(d)
                if(d.message){
                frm.set_value("user_id",frm.doc.user_id)
                frm.set_value("user_name",d.message.employee_name)
                frm.set_value("converted_by_designation",d.message.designation)
                frm.set_value("converted_by_mobile",d.message.cell_number)
                }
                }
        })
    },
        
    user_id(frm){
        frappe.call({
            method: "electra.utils.get_user_details",
            args:{
                "user": frm.doc.user_id
            },
            callback:function(d){
                if(d.message){
                frm.set_value("user_id",frm.doc.user_id)
                frm.set_value("user_name",d.message.employee_name)
                frm.set_value("designation",d.message.designation)
                frm.set_value("mobile_number",d.message.cell_number)
                }
                }
        })
    },
    
    refresh(frm){
        frm.trigger("get_credit_limit")
        var input = 'input[data-fieldname="item_code"][data-doctype="Quotation Item"]';
        var isFocus = false;
        frm.fields_dict.items.grid.wrapper.on('click', input, function(e) {
            if (!isFocus) {
                const item_code = e.currentTarget.value;
                frappe.call({
	        method: 'electra.custom.stock_popup',
	        args:{
	            'item_code':item_code
	        },
	        callback(d){
	           if (d.message){
	              frm.get_field("items_html").$wrapper.html(d.message);
	           }
	       }
	    })
            }
            isFocus = false;
        });

        frm.trigger("set_prepared_by")
        if(frm.doc.company){
		frm.trigger("set_series")
	    }
		},
		
	company(frm){
	    if(frm.doc.company){
	    frm.trigger("set_series")
	    }
	},
	set_series(frm){
	    frappe.call({
    		method: "electra.utils.get_series",
    		args: {
    			company: frm.doc.company,
    			doctype: frm.doc.doctype
    		},
    		callback: function (r) {
    			if (r) {
    			    frm.set_value('naming_series',r.message)
    			}
    		}
			});
	},
	create_contact(frm){
	    let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'Name',
            fieldname: 'name',
            fieldtype: 'Data'
        },
        {
            label: 'Email ID',
            fieldname: 'email_id',
            fieldtype: 'Data'
        },
        {
            label: 'Contact Number',
            fieldname: 'contact_number',
            fieldtype: 'Int'
        },
        // {
        //     label: 'Quotation To',
        //     fieldname: 'quotation_to',
        //     fieldtype: 'Link',
        //     options:'Doctype',
        //     default:'Customer'
        // },
        // {
        //     label: 'Link Name',
        //     fieldname: 'link_name',
        //     fieldtype: 'Dynamic Link',
        //     options:'link_doctype'
        // }
    ],
    primary_action_label: 'Submit',
    primary_action(values) {
        frappe.call({
            method:'electra.custom.create_contact',
            args:{
                'name': values.name,
                'email': values.email_id,
                'contact_no' :values.contact_number,
                'customer_name':frm.doc.party_name
                
            },
            
        callback(r){
            
        }
            
        })
        d.hide();
    }
});

d.show();
	    
	},
	setup(frm){
	    frm.trigger("set_prepared_by")
	},
    
    set_prepared_by(frm){
        if(frm.doc.__islocal){
        if(frm.doc.opportunity){
            frappe.call({
                method: "frappe.client.get",
                args:{
                    doctype: "Opportunity",
                    filters: {
						"name": frm.doc.opportunity
					},
					fields: ['converted_by']
                },
                callback:function(r){
                    frm.set_value("converted_by",r.message.converted_by)
                    frappe.call({
                        method: "electra.utils.get_user_details",
                        args:{
                            "user": r.message.converted_by
                        },
                        callback:function(d){
                            if(d.message){
                            frm.set_value("user_id",frm.doc.user_id)
                            frm.set_value("user_name",d.message.employee_name)
                            frm.set_value("designation",d.message.designation)
                            frm.set_value("mobile_number",d.message.cell_number)
                            frm.set_value("converted_by_designation",d.message.designation)
                            frm.set_value("converted_by_mobile",d.message.cell_number)
                            }
                        }
                    })
                }
            })
        }
        else{
            frm.set_value("user_id",frappe.session.user)
        }
        }
    },
    party_name(frm){
        frm.trigger("get_credit_limit")
    },
    quotation_to(frm){
        frm.trigger("get_credit_limit")
    },
    get_credit_limit(frm){
        $(frm.fields_dict.credit_limit.wrapper).empty();
        if(frm.doc.quotation_to == 'Customer' && frm.doc.party_name){
             
            frappe.call({
	        method: 'electra.utils.fetch_credit_limit',
	        args:{
	            "company" : frm.doc.company,
	            "customer" : frm.doc.party_name
	        },
	        callback(d){
	           if (d.message){
	            $(frm.fields_dict.credit_limit.wrapper).append(d.message);

	           }
	       }
	    })
        }
    },
    onload(frm){
        frm.trigger("set_prepared_by")
        frm.get_field("items_html").$wrapper.html();
	    if(frm.doc.__islocal){
	    if(frm.doc.cost_estimation){
	    frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Cost Estimation",
				filters: {
					"name": frm.doc.cost_estimation
				},
				fields:["*"]
			},
			callback: function (r) {
				if (r.message) {
				    frm.clear_table("scope_of_work")
				    $.each(r.message.master_scope_of_work,function(i,d){
				        frm.add_child("scope_of_work", {
						'msow': d.msow,
						'msow_desc': d.msow_desc,
						'total_cost':d.total_cost,
						'total_overheads':d.total_overheads,
						'total_business_promotion':d.total_business_promotion,
						'total_bidding_price': d.total_bidding_price,
						'qty':d.qty,
						'unit':d.unit,
						'unit_price':d.unit_price
					})
					frm.refresh_field('scope_of_work')
				    })
				}
			}
		});
	
		
	    frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Cost Estimation",
				filters: {
					"name": frm.doc.cost_estimation
				},
			},
			callback: function (r) {
			    if(frm.doc.__islocal){
			        frm.clear_table("items")
			        frm.clear_table("quotation_work_title_item")
				if (r.message) {
				    var qty = 0
				    var amount = 0
				    $.each(r.message.design_calculation,function(i,d){
				        console.log(r.message.design_calculation)
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'DESIGN',
						'qty': d.qty,
						'uom': d.unit,
						'description':  desc,
						'rate': d.unit_price,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				     if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'DESIGN',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				     }
				    
				    var qty = 0
				    var amount = 0
				    $.each(r.message.materials,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'MATERIALS',
						'qty': d.qty,
						'uom': d.unit,
						'description': desc,
				// 		'rate': d.unit_price,
				        'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'MATERIALS',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
				    var qty = 0
				    var amount = 0
				    $.each(r.message.finishing_work,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'FINISHING WORK',
						'qty': d.qty,
						'uom': d.unit,
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'FINISHING WORK',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
				    var qty = 0
				    var amount = 0
				    $.each(r.message.bolts_accessories,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'ACCESSORIES',
						'qty': d.qty,
						'uom': d.unit,
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'ACCESSORIES',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
				    var qty = 0
				    var amount = 0
				    $.each(r.message.installation_cost,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'INSTALLATION',
						'qty': d.qty,
						'uom': 'Nos',
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'INSTALLATION',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
					var qty = 0
				    var amount = 0
				    $.each(r.message.manpower_cost,function(i,d){
				        qty += d.total_workers
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.worker
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.worker,
						'item_name': d.worker,
						'work_title': 'MANPOWER',
						'qty': d.total_workers,
						'uom': 'Nos',
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'MANPOWER',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
					var qty = 0
				    var amount = 0
				    $.each(r.message.heavy_equipments,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'TOOLS/EQUIPMENTS/TRANSPORT',
						'qty': d.qty,
						'uom': d.unit,
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'TOOLS/EQUIPMENTS/TRANSPORT',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
				    
				    var qty = 0
				    var amount = 0
				    $.each(r.message.manpower_subcontract,function(i,d){
				        qty += d.qty
				        amount += d.amount
				        var desc = ''
				        if (d.description){
				            desc = d.description
				        }
				        else{
				            desc = d.item
				        }
				        frm.add_child("items", {
				        'msow':d.msow,
				        'ssow':d.ssow,
						'item_code': d.item,
						'item_name': d.item,
						'work_title': 'OTHERS',
						'qty': d.qty,
						'uom': d.unit,
						'description': desc,
						'rate': d.rate_with_overheads,
						'rate_with_overheads': d.rate_with_overheads,
						'amount_with_overheads': d.amount_with_overheads,
					})
					frm.refresh_field('items')
				    })
				    
				    if(qty > 0 ){
				    frm.add_child("quotation_work_title_item", {
						'item_name': 'OTHERS',
						'quantity': qty,
						'amount': amount
					})
					frm.refresh_field('quotation_work_title_item')
				    }
				    
				//     frm.add_child("items", {
				// 		'item_code': "Contigency",
				// 		'item_name': "Contigency",
				// 		'qty': 1,
				// 		'uom': 'Nos',
				// 		'description': "Contigency",
				// 		'rate': r.message.contigency,
				// 	})
				// 	frm.refresh_field('items')
					frm.add_child("items", {
						'item_code': "Profit",
						'item_name': "Profit",
						'qty': 1,
						'uom': 'Nos',
						'description': "Profit",
						'rate': r.message.total_amount_of_profit,
					})
					frm.refresh_field('items')
					frm.add_child("items", {
						'item_code': "Engineering Overhead",
						'item_name': "Engineering Overhead",
						'qty': 1,
						'uom': 'Nos',
						'description': "Engineering Overhead",
						'rate': r.message.total_amount_as_engineering_overhead,
					})
					frm.refresh_field('items')
					frm.add_child("items", {
						'item_code': "General Overhead",
						'item_name': "General Overhead",
						'qty': 1,
						'uom': 'Nos',
						'description': "General Overhead",
						'rate': r.message.total_amount_as_overhead,
					})
					frm.refresh_field('items')
					frm.add_child("items", {
						'item_code': "Business Promotion",
						'item_name': "Business Promotion",
						'qty': 1,
						'uom': 'Nos',
						'description': "Business Promotion",
						'rate': r.message.business_promotion,
					})
					frm.refresh_field('items')
				}
			    }
			}
		});
	    }
    }
    else{
        // if(frappe.user.has_role('HOD')){
        //     frm.add_custom_button(__("Show Valuation Rate"), function () {
        //         frappe.call({
        // 	        method: 'electra.utils.show_valuation_rate',
        // 	        args:{
        // 	            'items' : frm.doc.items,
        // 	            'company': frm.doc.company
        // 	        },
        // 	        callback(d){
        // 	           if (d.message){
        // 	               frappe.msgprint(d.message)
        // 	           }
        // 	       }
        // 	    })
        //     });
        // }
       
        frm.add_custom_button(__("Trading"), function () {
                if(frm.doc.parent_company){
                    var letter_head = frm.doc.parent_company
                }
                else{
                    var letter_head = frm.doc.company
                } 
                var f_name = frm.doc.name
                var print_format ="Quotation";
                 window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Quotation")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                    + "&letterhead=" + encodeURIComponent(letter_head) 
                   ));
            

            }, __("Print Quotation for"));
        
        frm.add_custom_button(__("Projects"), function () {
                if(frm.doc.parent_company){
                    var letter_head = frm.doc.parent_company
                }
                else{
                    var letter_head = frm.doc.company
                } 
                var f_name = frm.doc.name
                var print_format ="Projects Quotation";
                 window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                    + "doctype=" + encodeURIComponent("Quotation")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1"
                    + "&format=" + print_format
                    + "&no_letterhead=0"
                    + "&letterhead=" + encodeURIComponent(letter_head) 
                   ));
            

            }, __("Print Quotation for"));
    }
    },

	
	
		fetch(frm){
	    frappe.call({
	        method: 'electra.custom.get_stock_balance',
	        args:{
	            'item_table':frm.doc.items
	        },
	        callback(d){
	            frm.clear_table('stock_availability')
	            if (d.message){
	                $.each(d.message,function(i,v){
	                    frm.add_child('stock_availability',{
	                        'item_code':v[0],
	                        'item_name':v[1],
	                        'warehouse':v[2],
	                        'qty':v[3],
	                        'uom':v[4],
	                        'value':v[5]
	                    })
	                    frm.refresh_field('stock_availability')
	                })
	            }
	       }
	    })
	    
	     frappe.call({
	        method: 'electra.custom.get_previous_po',
	        args:{
	            'item_table':frm.doc.items
	        },
	        callback(d){
	            frm.clear_table('previous_po')
	            if (d.message){
	                $.each(d.message,function(i,v){
	                    frm.add_child('previous_po',{
	                        'item_code':v[0],
	                        'item_name':v[1],
	                        'supplier':v[2],
	                        'qty':v[3],
	                        'po_date':v[4],
	                        'amount':v[5],
	                        'purchase_order':v[6]
	                    })
	                    frm.refresh_field('previous_po')
	                })
	            }
	       }
	    })
	    
	    frappe.call({
	        method: 'electra.custom.get_out_qty',
	        args:{
	            'item_table':frm.doc.items
	        },
	        callback(d){
	            frm.clear_table('stock_out_qty')
	            if (d.message){
	                $.each(d.message,function(i,v){
	                    frm.add_child('stock_out_qty',{
	                        'item_code':v[0],
	                        'warehouse':v[1],
	                        'qty':v[2],
	                        'date':v[3],
	                        'out_type':v[4]
	                    })
	                    frm.refresh_field('stock_out_qty')
	                })
	            }
	       }
	    })
	},
	
		additional_discount_percentage(frm){
	    if (frm.doc.additional_discount_percentage){
	    frappe.call({
	        method: 'electra.custom.check_discount_percent',
	        args:{
	            
	            'discount': frm.doc.additional_discount_percentage
	        },
	        callback(r){
	            console.log(r.message)
	            if(r.message){
	            if(r.message != 'invalid'){
	                frappe.msgprint("Maximum discount percentage allowed for you is "+String(r.message)+ "%")
	                frm.set_value('additional_discount_percentage','')
	               
	            }
	            else{
	                frappe.msgprint("You are not authorised to give discount")
	                frm.set_value('additional_discount_percentage','')
	               
	            }
	        }
	        }
	    })
	}
	},
	discount_amount(frm){
	    var percent = (frm.doc.discount_amount * 100)/frm.doc.total
	   // frm.set_value('additional_discount_percentage',percent)
	    console.log(percent)
	     if (percent){
	    frappe.call({
	        method: 'electra.custom.check_discount_percent',
	        args:{
	            
	            'discount': percent
	        },
	        callback(r){
	            console.log(r.message)
	            if(r.message){
	            if(r.message != 'invalid'){
	                frappe.msgprint("Maximum discount percentage allowed for you is "+String(r.message)+ "%")
	                frm.set_value('additional_discount_percentage','')
	               
	            }
	            else{
	                frappe.msgprint("You are not authorised to give discount")
	                frm.set_value('additional_discount_percentage','')
	               
	            }
	        }
	        }
	    })
	}
	    
	    
	}
	
})

frappe.ui.form.on('Quotation Scope of Work', {
    qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.unit_price = row.total_bidding_price / row.qty
		frm.refresh_field('scope_of_work')
	},
	details(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		frappe.db.get_value('CE SOW', { 'cost_estimation': frm.doc.cost_estimation, 'msow': child.msow , 'ssow': '' }, 'name')
			.then(r => {
				if (r.message && Object.entries(r.message).length === 0) {
					frappe.route_options = {
						'cost_estimation': frm.doc.name,
						'msow': child.msow,
					}
					frappe.new_doc('CE SOW')
				}
				else {
					frappe.route_options = {
						'cost_estimation': frm.doc.name,
						'msow': child.msow,
					}
					frappe.set_route('Form', 'CE SOW', r.message.name)
				}
			})

	}
})

frappe.ui.form.on('Quotation Item', {
    
    item_code(frm,cdt,cdn) {
	    var child = locals[cdt][cdn]
	    if(child.item_code){
	  frm.trigger('fetch')
	  frappe.call({
	        method: 'electra.custom.stock_popup',
	        args:{
	            'item_code':child.item_code
	        },
	        callback(d){
	           if (d.message){
	              frm.get_field("items_html").$wrapper.html(d.message);
	           }
	       }
	    })
	    
	    }
	},
	items_remove(frm){
	    frm.trigger('fetch')
	},
	
	discount_percentage(frm,cdt,cdn){
        var child = locals[cdt][cdn]
	    if (child.discount_percentage){
	    frappe.call({
	        method: 'electra.custom.check_discount_percent',
	        args:{
	            'user':frappe.session.user,
	            'discount': child.discount_percentage
	        },
	        callback(r){
	            if(r.message){
	            if(r.message != 'invalid'){
	                frappe.msgprint("Maximum discount percentage allowed for you is "+String(r.message)+ "%")
	                child.discount_percentage = ''
	                frm.refresh_field('items')
	            }
	            else{
	                frappe.msgprint("You are not authorised to give discount")
	                child.discount_percentage = ''
	                frm.refresh_field('items')
	            }
	        }
	        }
	    })
	}
	},
	
	download(frm,cdt,cdn) {
	    var child = locals[cdt][cdn]
	    var f_name = child.item_code
        var url = frappe.urllib.get_full_url(
					'https://erp.nordencommunication.com/api/method/norden.utils.download_pdf?'
					+ "doctype=" + encodeURIComponent("Eyenor Datasheet")
                    + "&name=" + encodeURIComponent(f_name)
                    + "&trigger_print=1&format=Datasheet%202&no_letterhead=0"
                    )
		$.ajax({
			url: url,
			type: 'GET',
			success: function(result) {
				if(jQuery.isEmptyObject(result)){
					frappe.msgprint(__('No Records for these settings.'));
				}
				else{
					window.location = url;
				}
			}
		});
        
	}
	

})



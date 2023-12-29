// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product Search', {
	item_code(frm){
		if(frm.doc.item_code){
		frm.call('get_data').then(r=>{
			if (r.message) {
				frm.fields_dict.html.$wrapper.empty().append(r.message)
				frm.call('get_pod').then(r=>{
					frm.fields_dict.pod.$wrapper.empty().append(r.message)
				})
			}
		})	
			
		frm.call('get_data_perm').then(j=>{
			if (j.message) {
				frm.fields_dict.perm.$wrapper.empty().append(j.message)
			}
		})
	}	
	},
	onload(frm){
		var user_id = frappe.session.user
		console.log(user_id)
		if(user_id == "anoop@marazeemqatar.com"){
			frm.set_query('item_code', function(doc) {
				return {
					filters: {
						mss:1,
					}
				};
			});
		}
		else{
			frappe.db.get_value("Employee",{'user_id':user_id},'company')
			.then(r => {
				var value = r.message.company
				if(value == "KINGFISHER - SHOWROOM"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ktcc : 1,
								}
							};
						});
				}
							
				if(value == "MEP DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									mep : 1,
								}
							};
						});
				}
				if(value == "TRADING DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									tde : 1,
								}
							};
						});
				}
				if(value == "KINGFISHER TRADING AND CONTRACTING COMPANY"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									kt : 1,
								}
							};
						});
				}
				if(value == "ENGINEERING DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									eed : 1,
								}
							};
						});
				}
			
				if(value == "ELECTRA - BINOMRAN SHOWROOM"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ebo : 1,
								}
							};
						});
				}
				if(value == "MARAZEEM SECURITY SERVICES - HO"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									mssho : 1,
								}
							};
						});
				}
				if(value == "MARAZEEM SECURITY SERVICES - SHOWROOM"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									mss : 1,
								}
							};
						});
				}
				if(value == "ELECTRICAL DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ede : 1,
								}
							};
						});
				}
				if(value == "INTERIOR DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ine : 1,
								}
							};
						});
				}
				if(value == "STEEL DIVISION - ELECTRA"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									sde : 1,
								}
							};
						});
				}
				if(value == "ELECTRA  - NAJMA SHOWROOM"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ens : 1,
								}
							};
						});
				}
				if(value == "ELECTRA - BARWA SHOWROOM"){
						frm.set_query('item_code', function(doc) {
							return {
								filters: {
									ebs : 1,
								}
							};
						});
				}
			})
		}
    },
})
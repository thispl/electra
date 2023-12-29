frappe.ui.form.on('Project Budget', {
	work_title(frm){
		frm.clear_table('work_title_summary')
		var qty = 0
		var amount = 0
		$.each(frm.doc.design, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})
		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'DESIGN',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.materials, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})
		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'SUPPLY MATERIALS',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.finishing_work, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'FINISHING WORK',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.bolts_accessories, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'ACCESSORIES',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.installation, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'INSTALLATION',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.manpower, function (i, d) {
			qty += d.total_workers
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'MANPOWER',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}

		var qty = 0
		var amount = 0
		$.each(frm.doc.heavy_equipments, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'TOOLS/EQUIPMENTS/TRANSPORT/OTHERS',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}


		var qty = 0
		var amount = 0
		$.each(frm.doc.manpower_subcontract, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'SUBCONTRACT',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}
		
		var qty = 0
		var amount = 0
		$.each(frm.doc.finished_goods, function (i, d) {
			qty += d.qty
			amount += d.amount_with_overheads
		})

		if (qty > 0) {
			frm.add_child("work_title_summary", {
				'item_name': 'FINISHED GOODS',
				'quantity': qty,
				'amount': amount
			})
			frm.refresh_field('work_title_summary')
		}
	},
	update_msow(frm){
		frappe.call({
			method:'electra.electra.doctype.project_budget.project_budget.update_msows',
			args:{
				document:frm.doc.name,
				sales_order:frm.doc.sales_order
			},
		});
	},
	before_workflow_action: async (frm) => {
		if(frm.doc.workflow_state == "Draft"){
			let promise = new Promise((resolve, reject) => {
				if (frm.selected_workflow_action == "Approve") {
					frappe.run_serially([
						() => {frm.trigger("get_pb_sow")},
						() => frm.save(),						
						() => {frm.trigger("work_title")},
						() => frm.save(),
						() => {frm.trigger("msow_update")},
						// () => frm.save(),
						() => {frm.trigger("combine_tables")},
						// () => frm.save(),
						() => {frm.trigger("update_name")},
						() => frm.save(),
						() => resolve()
					])
				}
			});
			await promise.catch(() => frappe.throw());
		}
		if(frm.doc.workflow_state == "In Review"){
			let promise = new Promise((resolve, reject) => {
				if (frm.selected_workflow_action == "Approve") {
					frm.trigger("update_so")
				}
				resolve();
			});
			await promise.catch(() => frappe.throw());
		}
	},
	revision(frm){
		$.each(frm.doc.master_scope_of_work,function(i,j){
			j.revision = frm.doc.revision
		})
		frm.refresh_field("master_scope_of_work")
	},
	refresh(frm) {
		if (frm.doc.total_bidding_price){
			frm.add_custom_button(__("Total Cost"), function () {
				var f_name = frm.doc.name
				frappe.call({
					method:'electra.electra.doctype.project_budget.project_budget.get_data',
					args:{
						cmp:frm.doc.company,
						tc:frm.doc.total_overhead,
						ec:frm.doc.engineering_overhead,
						cp:frm.doc.contigency_percent,
						gpp:frm.doc.gross_profit_percent,
						netp:frm.doc.net_profit_percent,
						tcc:frm.doc.total_amount_as_overhead,
						tec:frm.doc.total_amount_as_engineering_overhead,
						cpc:frm.doc.contigency,
						gppc:frm.doc.gross_profit_amount,
						neta:frm.doc.net_profit_amount,
						tpb:frm.doc.total_business_promotion,
						tcp:frm.doc.total_cost_of_the_project,
						dis:frm.doc.discount_amount,
						tbp:frm.doc.total_bidding_price,
					},
					callback (r) {
						if (r.message) {
							let d = new frappe.ui.Dialog({
								size:"small",
								
								fields: [
									{
										label: 'Total Cost',
										fieldname: 'total_cost',
										fieldtype: 'HTML'
									},
								],
										
							});
							d.fields_dict.total_cost.$wrapper.html(r.message);
							d.show();	
						}
					}
				});      
				
		})
	}
		
		// // frm.trigger('workflow_state')
		frm.add_custom_button(__('Combine'),
		function () {
			frappe.run_serially([
				() => {frm.trigger("get_pb_sow")},
				() => frm.save(),						
				() => {frm.trigger("work_title")},
				() => frm.save(),
				() => {frm.trigger("msow_update")},
				// () => frm.save(),
				() => {frm.trigger("combine_tables")},
				() => frm.save(),
				() => {frm.trigger("update_name")},
				() => frm.save(),
			])
			// frm.trigger("update_msow")
			// frm.trigger("work_title")
			// frm.trigger("combine_tables")
			// frm.trigger("update_items")
			// frm.trigger('update_name')
		});
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
		
	},
	setup(frm){
		frm.get_docfield('item_table').allow_bulk_edit = 1
	},
	update_name(frm){
		$.each(frm.doc.item_table,function(i,k){
		frappe.call({
			method:"electra.custom.get_name_pb",
			args:{
				'so':frm.doc.sales_order,
			},
			callback(r){
				if(r){
					$.each(r.message,function(i,d){
						if(k.item == d.item_code){
							k.docname = d.name
						}
					})
				}
			}
		})
		// frm.save()
	})
	},
	combine_tables(frm){
		frm.clear_table('item_table')		
		$.each(frm.doc.design,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.materials,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.finishing_work,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.bolts_accessories,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.installation,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.heavy_equipments,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.others,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})
		$.each(frm.doc.finished_goods,function(i,d){
			frm.add_child('item_table',{
				'item':d.item,
				'msow':d.msow,
				'item_name':d.item_name,
				'surface_area':d.surface_area,
				'description':d.description,
				'unit':d.unit,
				'qty':d.qty,
				'cost':d.cost,
				'cost_amount':d.cost_amount,
				'unit_price':d.unit_price,
				'amount':d.amount,
				'difference':d.difference,
				'rate_with_overheads':d.rate_with_overheads,
				'amount_with_overheads':d.amount_with_overheads
			})
			frm.refresh_field('item_table')
		})		
		$.each(frm.doc.manpower,function(i,d){
			frm.add_child('item_table',{
				"item": d.worker,
				'msow':d.msow,
				"item_name": d.worker,
				"qty": d.total_workers,
				"rate": d.rate_with_overheads,
				'cost':d.cost,
				'unit_price':d.rate,
				"cost_amount":d.cost_amount,
				"estimated_cost":d.estimated_cost,
				"estimated_amount":d.estimated_amount,
				"amount": d.amount,
				"amount_with_overheads": d.amount_with_overheads,
				"rate_with_overheads":d.rate_with_overheads,
			})
			frm.refresh_field('item_table')
		})	
	},
	onload(frm) {
		if (frm.doc.__islocal) {
		// frm.set_value('date_of_budget',frappe.datetime.nowdate())
		frappe.db.get_value('Sales Order',frm.doc.sales_order,'docstatus')
        .then(r => {
            var value = r.message.docstatus
			if(value == 1){
				if(frm.doc.amended_from){
					let d = new frappe.ui.Dialog({
						title: 'Choose the option to revise',
						fields: [
							{
								label: 'Revision',
								fieldname:'revision',
								reqd:1,
								fieldtype:'Select',
								options:'PB - Revision\nSO - Revision',
								description:'Please Select one Option'
							},
							{
								label: 'Message',
								fieldname: 'message',
								fieldtype: 'HTML',
								options: '<h6 style="color: #27456b;"><b>PB - Revision:</b>&nbsp;LPO amount never changes,changes will be adjusted only in profit</h6><br><h6 style="color: #27456b;"><b>SO - Revision:</b>&nbsp;LPO amount will be updated with the update in PB</h6>'
							},
							{
								label: 'Remarks',
								fieldname:'remarks',
								reqd:1,
								fieldtype:'Small Text',
							},
							{
								fieldname:'section',
								fieldtype:'Section Break',
								hidden:1
							},
							{
								label: 'Date',
								fieldname:'date',
								fieldtype:'Date',
								default: frappe.datetime.now_date()
							},
							{
								label: 'Time',
								fieldname:'time',
								fieldtype:'Time',
								default: frappe.datetime.now_time()
							},
						],
						primary_action_label: 'Submit',
						primary_action(values) {
							if(frm.set_value('revision',values.revision)){
								if(frm.doc.revision == "PB - Revision"){
									var cal = frm.doc.pb_revision + 1
									frm.set_value('pb_revision',cal)
								}
								if(frm.doc.revision == "SO - Revision"){
									var cal = frm.doc.so_revision + 1
									frm.set_value('so_revision',cal)
									frm.set_value('pb_revision',cal)
								}
								d.hide();
							}
							var value = values.remarks;
							var Date = values.date;
							var Time = values.time;
							let newRemark = {
								date:Date,
								time:Time,
								remarks: value, 
							};
							frm.add_child('remark_table', newRemark);
							// frm.doc.remark_table.push(newRemark);
							frm.refresh_field('remark_table');
							
							}
					});
					
					d.show();
				}
			}
		})
			if (frm.doc.sales_order) {
				frm.trigger("get_so_data")
			}
		}
		if (!frm.doc.__islocal) {
			if (frm.doc.sales_order) {
				frm.trigger("get_pb_msow")
			}
		}


	},
	company(frm) {
		if (frm.doc.company) {
			frm.trigger("set_series")
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
	cost_estimation(frm) {
		if (frm.doc.docstatus != 1) {
			// frm.trigger("get_ce_data")

		}
	},

	get_pb_msow(frm) {
		if (frm.doc.master_scope_of_work) {
			$.each(frm.doc.master_scope_of_work, function (i, d) {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						'doctype': 'PB SOW',
						filters: {
							'project_budget': frm.doc.name,
							'msow': d.msow,
							'ssow': ''
						},
						fields: ['*']
					},
					callback(r) {
						$.each(r.message, function (j, k) {
							d.qty = k.qty
							d.unit = k.uom
							d.total_overhead = k.overhead_percent
							d.total_amount_as_overhead = k.overhead_amount
							d.gross_profit_percent = k.pb_gross_profit_percent //
							d.gross_profit_amount = k.pb_gross_profit_amount // 
							if(frm.doc.company == "MEP DIVISION - ELECTRA"){
								d.net_profit_percent = k.pb_mep_net_profit_percent
								d.net_profit_amount = k.pb_mep_net_profit_amount
							}
							else{
								d.net_profit_percent = k.pb_net_profit_percent
								d.net_profit_amount = k.pb_net_profit_amount
							}
							d.contigency_percent = k.pb_contigency_percent //
							d.contigency = k.pb_contigency_amount //
							d.engineering_overhead = k.pb_engineering_overhead_percent //
							d.total_amount_as_engineering_overhead = k.pb_engineering_overhead_amount //
							d.total_overheads = k.pb_overhead_amount + k.pb_contigency_amount + k.pb_engineering_overhead_amount
							d.total_business_promotion = k.pb_business_promotion_amount
							d.total_cost = k.pb_total_cost
						})

					}
				})
				frm.refresh_field("master_scope_of_work")
			})
		}
	},

	get_so_data(frm) {
		frm.clear_table("master_scope_of_work")
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Sales Order",
				filters: {
					"name": frm.doc.sales_order
				},
				fields: ["*"]
			},
			callback: function (r) {
				if (r.message) {
					$.each(r.message.scope_of_work, function (i, d) {
						frm.add_child("master_scope_of_work", {
							'msow': d.msow,
							'msow_desc': d.msow_desc,
							'total_cost': d.total_cost,
							'total_overheads': d.total_overheads,
							'total_business_promotion': d.total_business_promotion,
							'total_bidding_price': d.total_bidding_price,
							'qty': d.qty,
							'discount': d.discount,
							'unit': d.unit,
							'unit_price': d.unit_price
						})
						frm.refresh_field('master_scope_of_work')
					})
				}
			}
		})
	},

	get_pb_sow(frm) {
		frm.clear_table('design')
		frm.clear_table('materials')
		frm.clear_table('finishing_work')
		frm.clear_table('bolts_accessories')
		frm.clear_table('installation')
		frm.clear_table('finished_goods')
		frm.clear_table('manpower')
		frm.clear_table('heavy_equipments')
		frm.clear_table('others')
		var design_cost = 0
		var design_amount = 0
		var design_amount_with_overheads = 0
		var design_profit = 0
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				'doctype': 'PB SOW',
				filters: {
					'project_budget': frm.doc.name,
				},
				fields: ['*']
			},
			callback(r) {
				$.each(r.message, function (i, d) {
					frappe.call({
						method: "frappe.client.get",
						args: {
							'doctype': 'PB SOW',
							filters: {
								'name': d.name,
							},
						},
						callback(r) {
							// frm.clear_table('design')
							$.each(r.message.design, function (i, c) {
								frm.add_child('design', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('design')

							// frm.clear_table('materials')
							$.each(r.message.materials, function (i, c) {
								frm.add_child('materials', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('materials')
							// frm.clear_table('mep_materials')
							$.each(r.message.mep_materials, function (i, c) {
								frm.add_child('materials', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('materials')
							// frm.clear_table('finishing_work')
							$.each(r.message.finishing_work, function (i, c) {
								frm.add_child('finishing_work', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('finishing_work')
							// frm.clear_table('bolts_accessories')
							$.each(r.message.bolts_accessories, function (i, c) {
								frm.add_child('bolts_accessories', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('bolts_accessories')

							// frm.clear_table('installation')
							$.each(r.message.installation, function (i, c) {
								frm.add_child('installation', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('installation')

							// frm.clear_table('manpower')
							$.each(r.message.manpower, function (i, c) {
								frm.add_child('manpower', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'worker': c.worker,
									'rate':c.rate,
									'total_workers': c.total_workers,
									'unit_price': c.unit_price,
									'working_hours': c.working_hours,
									'days': c.days,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('manpower')

							// frm.clear_table('others')
							$.each(r.message.others, function (i, c) {
								frm.add_child('others', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('others')

							// frm.clear_table('finished_goods')
							$.each(r.message.finished_goods, function (i, c) {
								frm.add_child('finished_goods', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'bom': c.bom,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('finished_goods')

							// frm.clear_table('heavy_equipments')
							$.each(r.message.heavy_equipments, function (i, c) {
								frm.add_child('heavy_equipments', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'item_group': c.item_group,
									'item': c.item,
									'item_name': c.item_name,
									'description': c.description,
									'unit': c.unit,
									'qty': c.qty,
									'unit_price': c.unit_price,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount,
									'cost': c.cost,
									'cost_amount': c.cost_amount,
									'estimated_cost':c.estimated_cost,
									'estimated_amount':c.estimated_amount
								})
							})
							frm.refresh_field('heavy_equipments')

							// $.each(r.message.others, function (i, c) {
							// 	frm.add_child('others', {
							// 		'msow': r.message.msow,
							// 		'ssow': r.message.ssow,
							// 		'item_group': c.item_group,
							// 		'item': c.item,
							// 		'item_name': c.item_name,
							// 		'description': c.description,
							// 		'unit': c.unit,
							// 		'qty': c.qty,
							// 		'unit_price': c.unit_price,
							// 		'rate_with_overheads': c.rate_with_overheads,
							// 		'amount_with_overheads': c.amount_with_overheads,
							// 		'amount': c.amount,
							// 		'cost': c.cost,
							// 		'cost_amount': c.cost_amount,
							// 		'estimated_cost':c.estimated_cost,
							// 		'estimated_amount':c.estimated_amount
							// 	})
							// })
							// frm.refresh_field('others')
						}
					})
				})
			}
		})
	},
	update_items(frm){		
		frappe.db.get_value('Sales Order',frm.doc.sales_order,'delivery_date')
        .then(r => {
            var value = r.message.delivery_date
			frm.set_value('delivery_date',value)
		})
		var data = []
		frappe.db.get_value('Warehouse',{'company':frm.doc.company,'default_for_stock_transfer':1},'name')
        .then(r => {
            var value = r.message.name
			frm.set_value('warehouse',value)
		})		
		frm.doc.item_table.forEach(d => {
			data.push({
				"msow":d.msow,
				"docname":d.docname,
				"name": d.name,
				"item_code": d.item,
				"delivery_date": frm.doc.delivery_date,
				"conversion_factor": d.conversion_factor,
				"qty": d.qty,
				"rate": d.rate_with_overheads,
				"uom": d.uom,
				"warehouse" : frm.doc.warehouse,
			});
		})
		console.log(data)
		const item_table = frm.doc.item_table;
		frappe.call({
			method: 'erpnext.controllers.accounts_controller.update_child_qty_rate',
			freeze: true,
			args: {
				'parent_doctype': "Sales Order",
				'trans_items': data,
				'parent_doctype_name': frm.doc.sales_order,
			},
			callback: function() {
				frm.reload_doc();
			}
		});
	},
	update_so(frm){
		frappe.db.get_value('Sales Order',frm.doc.sales_order,'docstatus')
		.then(r => {
			var value = r.message.docstatus
			if(frm.doc.amended_from){
				if(value == 1){
					frappe.call({
						method:'electra.electra.doctype.project_budget.project_budget.update_msows',
						args:{
							document:frm.doc.name,
							sales_order:frm.doc.sales_order
						},
						callback(r){
							frm.trigger("update_items")
						}
					});
				}			
			}				
		})	
	},
	// update_while_submission(frm){
	// 	frappe.db.get_value('Sales Order',frm.doc.sales_order,'docstatus')
	// 	.then(r => {
	// 		var value = r.message.docstatus
	// 		if(frm.doc.amended_from){
	// 			if(value == 1){
	// 				frm.trigger("update_items")
	// 				frm.set_value("update_check",1)
	// 			}
	// 		}
	// 	})
	// },
	msow_update(frm){
		$.each(frm.doc.master_scope_of_work, function (i, d) {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					'doctype': 'PB SOW',
					filters: {
						'project_budget': frm.doc.name,
						'msow': d.msow,
						'ssow': ''
					},
					fields: ['*']
				},
				callback(r) {
					$.each(r.message, function (j, k) {
						d.qty = k.qty
						d.unit = k.uom
						d.total_overhead = k.total_overhead
						d.total_amount_as_overhead = k.total_amount_as_overhead
						d.total_profit = k.total_profit
						d.total_amount_of_profit = k.total_amount_of_profit
						d.contigency_percent = k.contigency_percent
						d.contigency = k.contigency
						d.engineering_overhead = k.engineering_overhead
						d.total_amount_as_engineering_overhead = k.total_amount_as_engineering_overhead
						d.total_overheads = k.total_amount_as_overhead + k.total_amount_of_profit + k.contigency + k.total_amount_as_engineering_overhead
						d.total_profit_amount = k.total_profit_amount
						d.total_profit_percent = k.total_profit_percent
						d.total_business_promotion = k.business_promotion
						d.total_cost = k.total_cost
						d.total_bidding_price = k.pb_bidding_amount
						d.unit_price = k.pb_bidding_unit_rate
						
					})

				}
			})
			frm.refresh_field("master_scope_of_work")
		})
	},
	validate(frm) {
		var total_bidding_price = 0
		var total_amount_as_overhead = 0
		var total_amount_as_engineering_overhead = 0
		var contigency = 0
		var total_amount_of_profit = 0
		var total_cost = 0
		var total_overhead = 0
		var contigency_percent = 0
		var engineering_overhead = 0
		var total_business_promotion = 0
		var total_overheads = 0
		var discount = 0
		var total_net_profit_amount = 0
		var total_net_profit_percent = 0
		var total_gross_profit_percent = 0
		var total_gross_profit_amount = 0
		if (frm.doc.master_scope_of_work) {
			// frm.trigger("get_pb_msow")
			$.each(frm.doc.master_scope_of_work, function (i, d) {
				total_amount_as_overhead += d.total_amount_as_overhead
				contigency += d.contigency
				total_amount_as_engineering_overhead += d.total_amount_as_engineering_overhead
				// total_overheads += d.total_overheads
				total_business_promotion += d.total_business_promotion
				total_cost += d.total_cost
				discount += d.discount
				total_bidding_price += d.total_bidding_price
				total_net_profit_percent += d.net_profit_percent
				total_net_profit_amount += d.net_profit_amount
				total_gross_profit_percent += d.gross_profit_percent
				total_gross_profit_amount += d.gross_profit_amount
			})
			total_overhead = (total_amount_as_overhead / total_cost) * 100
			contigency_percent = (contigency / total_cost) * 100
			engineering_overhead = (total_amount_as_engineering_overhead / total_cost) * 100
			total_overheads = total_amount_as_overhead + total_amount_of_profit + contigency + total_amount_as_engineering_overhead
			frm.set_value('total_business_promotion',total_business_promotion)
			frm.set_value("total_amount_as_overhead", total_amount_as_overhead)
			frm.set_value("discount_amount", discount)
			frm.set_value("contigency", contigency)
			frm.set_value("total_amount_as_engineering_overhead", total_amount_as_engineering_overhead)
			frm.set_value("total_overhead", total_overhead)
			frm.set_value("net_profit_percent", total_net_profit_percent)
			frm.set_value("net_profit_amount", total_net_profit_amount)
			frm.set_value("gross_profit_percent", total_gross_profit_percent)
			frm.set_value("gross_profit_amount", total_gross_profit_amount)
			frm.set_value("contigency_percent", contigency_percent)
			frm.set_value("engineering_overhead", engineering_overhead)

			// overall totals
			frm.set_value("total_cost_of_the_project", total_cost)
			frm.set_value("total_bidding_price", total_bidding_price)
		}
		// frm.trigger("msow_update")

		$.each(frm.doc.master_scope_of_work, function (i, d) {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					'doctype': 'PB SOW',
					filters: {
						'project_budget': frm.doc.name,
						'msow': d.msow,
						'ssow': ''
					},
					fields: ['*']
				},
				callback(r) {
					$.each(r.message, function (j, k) {
						d.qty = k.qty
						d.unit = k.uom
						d.total_overhead = k.total_overhead
						d.total_amount_as_overhead = k.total_amount_as_overhead
						d.total_profit = k.total_profit
						d.total_amount_of_profit = k.total_amount_of_profit
						d.contigency_percent = k.contigency_percent
						d.contigency = k.contigency
						d.engineering_overhead = k.engineering_overhead
						d.total_amount_as_engineering_overhead = k.total_amount_as_engineering_overhead
						d.total_overheads = k.total_amount_as_overhead + k.total_amount_of_profit + k.contigency + k.total_amount_as_engineering_overhead
						d.total_profit_amount = k.total_profit_amount
						d.total_profit_percent = k.total_profit_percent
						d.total_business_promotion = k.business_promotion
						d.total_cost = k.total_cost
						d.total_bidding_price = k.pb_bidding_amount
						d.unit_price = k.pb_bidding_unit_rate
						
					})

				}
			})
			frm.refresh_field("master_scope_of_work")
		})
		var estimated_amount = 0
		var budgeted_amount = 0
		$.each(frm.doc.items, function (i, d) {
			estimated_amount += d.estimated_amount
			budgeted_amount += d.amount
		})
		if (!isNaN(estimated_amount)) {
			frm.set_value("total_estimated_amount", estimated_amount)
		}
		else {
			frm.set_value("total_estimated_amount", 0)
		}

		if (!isNaN(budgeted_amount)) {
			frm.set_value("total_budgeted_amount", budgeted_amount)
		}
		else {
			frm.set_value("total_budgeted_amount", 0)
		}


	}
})
frappe.ui.form.on('Budget Scope of Work', {
	view(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		frappe.db.get_value('PB SOW', { 'cost_estimation': frm.doc.name, 'msow': child.msow, 'ssow': '' }, 'name')
			.then(r => {
				frappe.route_options = {
					'cost_estimation': frm.doc.name,
					'msow': child.msow,
					'qty': child.qty,
					'uom': child.unit,
				}
				frappe.set_route('Form', 'PB SOW', r.message.name)

			})

	},
	budget(frm, cdt, cdn) {
		frm.save()
		var child = locals[cdt][cdn]

		frappe.db.get_value('PB SOW', { 'project_budget': frm.doc.name, 'msow': child.msow, 'ssow': '' }, 'name')
			.then(r => {
				if (r.message && Object.entries(r.message).length === 0) {
					frappe.route_options = {
						'project_budget': frm.doc.name,
						'cost_estimation': frm.doc.cost_estimation,
						'sales_order': frm.doc.sales_order,
						'company': frm.doc.company,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
					}
					frappe.new_doc('PB SOW')
				}
				else {
					frappe.route_options = {
						'project_budget': frm.doc.name,
						'cost_estimation': frm.doc.cost_estimation,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
					}
					frappe.set_route('Form', 'PB SOW', r.message.name)
				}
			})

	}
})
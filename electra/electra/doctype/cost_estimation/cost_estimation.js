frappe.ui.form.on('Cost Estimation', {
	add_sub(frm) {
		frm.save()
	},
	update_sub(frm) {
		frm.save()
	},
	setup(frm) {
		frm.set_query("company", function () {
			return {
				filters: {
					'has_project': 1
				}
			};
		});
	},
	lead_customer(frm) {
		if (frm.doc.cost_estimation_for == 'Customer') {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Customer",
					filters: {
						"name": frm.doc.lead_customer
					},
					fields: ['customer_name']
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("lead_customer_name", r.message.customer_name)
					}
				}
			});
		}
		if (frm.doc.cost_estimation_for == 'Lead') {
			frappe.call({
				method: "frappe.client.get",
				args: {
					doctype: "Lead",
					filters: {
						"name": frm.doc.lead_customer
					},
					fields: ['organization_name']
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("lead_customer_name", r.message.organization_name)
					}
				}
			});
		}
	},
	onload(frm) {
		if (frm.doc.docstatus == 0) {
			if (frm.doc.master_scope_of_work) {
				$.each(frm.doc.master_scope_of_work, function (i, d) {
					frappe.call({
						method: "frappe.client.get_list",
						args: {
							'doctype': 'CE SOW',
							filters: {
								'cost_estimation': frm.doc.name,
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
								d.net_profit_percent = k.net_profit_percent + k.mep_net_profit_percent
								d.net_profit_amount = k.net_profit_amount + k.mep_net_profit_amount
								d.gross_profit_percent = k.gross_profit_percent
								d.gross_profit_amount = k.gross_profit_amount
								d.contigency_percent = k.contigency_percent
								d.contigency = k.contigency
								d.engineering_overhead = k.engineering_overhead
								d.total_amount_as_engineering_overhead = k.total_amount_as_engineering_overhead
								d.total_overheads = k.total_amount_as_overhead + k.contigency + k.total_amount_as_engineering_overhead
								d.total_business_promotion = k.business_promotion_amount
								d.total_cost = k.total_cost
								d.total_bidding_price = k.total_bidding_price
								d.unit_price = k.unit_price
							})

						}
					})
					frm.refresh_field("master_scope_of_work")
				})
				frm.trigger('get_ce_sow')
			}
		}



	},
	get_ce_sow(frm) {
		frm.clear_table('design_calculation')
		frm.clear_table('materials')
		frm.clear_table('finishing_work')
		frm.clear_table('bolts_accessories')
		frm.clear_table('installation')
		frm.clear_table('manpower')
		frm.clear_table('heavy_equipments')
		frm.clear_table('manpower_subcontract')
		var design_cost = 0
		var design_amount = 0
		var design_amount_with_overheads = 0
		var design_profit = 0
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				'doctype': 'CE SOW',
				filters: {
					'cost_estimation': frm.doc.name,
				},
				// fields:['*']
			},
			callback(r) {
				$.each(r.message, function (i, d) {
					frappe.call({
						method: "frappe.client.get",
						args: {
							'doctype': 'CE SOW',
							filters: {
								'name': d.name,
							},
						},
						callback(r) {
							$.each(r.message.design, function (i, c) {
								frm.add_child('design_calculation', {
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
									'amount': c.amount
								})
							})
							frm.refresh_field('design_calculation')

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
									'amount': c.amount
								})
							})
							frm.refresh_field('materials')

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
									'amount_with_overheads': c.amount,
									'amount': c.amount
								})
							})
							frm.refresh_field('materials')

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
									'amount': c.amount
								})
							})
							frm.refresh_field('finishing_work')

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
									'amount': c.amount
								})
							})
							frm.refresh_field('bolts_accessories')

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
									'amount': c.amount
								})
							})
							frm.refresh_field('installation')

							$.each(r.message.manpower, function (i, c) {
								frm.add_child('manpower', {
									'msow': r.message.msow,
									'ssow': r.message.ssow,
									'worker': c.worker,
									'total_workers': c.total_workers,
									'unit_price': c.unit_price,
									'working_hours': c.working_hours,
									'days': c.days,
									'rate_with_overheads': c.rate_with_overheads,
									'amount_with_overheads': c.amount_with_overheads,
									'amount': c.amount
								})
							})
							frm.refresh_field('manpower')

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
									'amount': c.amount
								})
							})
							frm.refresh_field('heavy_equipments')

							$.each(r.message.others, function (i, c) {
								frm.add_child('manpower_subcontract', {
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
									'amount': c.amount
								})
							})
							frm.refresh_field('manpower_subcontract')
						}
					})
				})
				frm.set_value("design_cost", design_cost)
				frm.set_value("design_amount", r.message.design_amount)
				frm.set_value("design_amount_with_overheads", r.message.design_amount_with_overheads)
				frm.set_value("design_profit", r.message.design_profit)
			}
		})

		// frappe.call({
		// 	method: "frappe.client.get_list",
		// 	args: {
		// 		'doctype': 'CE SSOW',
		// 		filters: {
		// 			'cost_estimation': frm.doc.name,
		// 		},
		// 		// fields:['*']
		// 	},
		// 	callback(r) {
		// 		$.each(r.message, function (i, d) {
		// 			frappe.call({
		// 				method: "frappe.client.get",
		// 				args: {
		// 					'doctype': 'CE SSOW',
		// 					filters: {
		// 						'name': d.name,
		// 					},
		// 				},
		// 				callback(r) {
		// 					$.each(r.message.design, function (i, c) {
		// 						frm.add_child('design_calculation', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('design_calculation')

		// 					$.each(r.message.materials, function (i, c) {
		// 						frm.add_child('materials', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('materials')

		// 					$.each(r.message.finishing_work, function (i, c) {
		// 						frm.add_child('finishing_work', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('finishing_work')

		// 					$.each(r.message.bolts_accessories, function (i, c) {
		// 						frm.add_child('bolts_accessories', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('bolts_accessories')

		// 					$.each(r.message.installation, function (i, c) {
		// 						frm.add_child('installation', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('installation')

		// 					$.each(r.message.manpower, function (i, c) {
		// 						frm.add_child('manpower', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'worker': c.worker,
		// 							'total_workers': c.total_workers,
		// 							'unit_price': c.unit_price,
		// 							'working_hours': c.working_hours,
		// 							'days': c.days,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('manpower')

		// 					$.each(r.message.heavy_equipments, function (i, c) {
		// 						frm.add_child('heavy_equipments', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('heavy_equipments')

		// 					$.each(r.message.others, function (i, c) {
		// 						frm.add_child('manpower_subcontract', {
		// 							'msow': c.msow,
		// 							'ssow': c.ssow,
		// 							'item_group': c.item_group,
		// 							'item': c.item,
		// 							'item_name': c.item_name,
		// 							'description': c.description,
		// 							'unit': c.unit,
		// 							'qty': c.qty,
		// 							'unit_price': c.unit_price,
		// 							'amount': c.amount
		// 						})
		// 					})
		// 					frm.refresh_field('manpower_subcontract')
		// 				}
		// 			})
		// 		})
		// 	}
		// })
		// frm.save()
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
	refresh(frm) {
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
		if (frm.doc.__islocal) {
			frm.set_value("date_of_estimation", frappe.datetime.nowdate())
		}

		if (frm.doc.docstatus == 1) {
		frm.add_custom_button(__('Quotation'),
			function () {
				if(frm.doc.amended_from){
					frappe.db.get_value('Quotation', { 'cost_estimation': frm.doc.amended_from}, 'name')
					.then(r => {
						if (r.message && Object.entries(r.message).length === 0) {
							frappe.model.open_mapped_doc({
								method: "electra.custom.make_quotation",
								frm: cur_frm
							})
						}
						else {
							frappe.set_route('Form', 'Quotation', r.message.name)
							console.log(r.message.name)			
						}


					})
				}	
				else{
					frappe.db.get_value('Quotation', { 'cost_estimation': frm.doc.name }, 'name')
					.then(r => {
						if (r.message && Object.entries(r.message).length === 0) {
							frappe.model.open_mapped_doc({
								method: "electra.custom.make_quotation",
								frm: cur_frm
							})
						}
						else {
							frappe.set_route('Form', 'Quotation', r.message.name)
							
						}


					})
				}
				
			}, __('Create/Edit'));
		}
	},
	onload_after_render(frm) {
		frm.trigger('total_calculation')
	},
	validate(frm) {
		// frm.trigger("total_design_calculation")
		// frm.trigger("total_material_calculation")
		// frm.trigger("total_finishing_work_calculation")
		// frm.trigger("total_bolts_accessories_calculation")
		// frm.trigger("total_installation_cost_calculation")
		// frm.trigger("total_manpower_cost_calculation")
		// frm.trigger("total_heavy_equipments_calculation")
		// frm.trigger("total_transportation_calculation")
		// frm.trigger("total_manpower_subcontract_calculation")
		// if (frm.doc.total_installation_cost && frm.doc.total_manpower_cost) {
		// 	var a = frm.doc.total_installation_cost
		// 	var b = frm.doc.total_manpower_cost
		// 	var diff_percent = 100 * Math.abs((a - b) / ((a + b) / 2));
		// 	if (diff_percent > 5) {
		// 		frappe.msgprint('Variation between Manpower Cost and Installation Cost should not be less than 5 %')
		// 		frappe.validated = false
		// 	}
		// }
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
		var total_net_profit_amount = 0
		var total_net_profit_percent = 0
		var total_gross_profit_percent = 0
		var total_gross_profit_amount = 0
		if (frm.doc.master_scope_of_work) {
			$.each(frm.doc.master_scope_of_work, function (i, d) {
				if (d.optional == 0) {
					total_amount_as_overhead += d.total_amount_as_overhead
					contigency += d.contigency
					total_amount_as_engineering_overhead += d.total_amount_as_engineering_overhead
					total_overheads += d.total_overheads
					total_business_promotion += d.total_business_promotion
					total_cost += d.total_cost
					total_bidding_price += d.total_bidding_price
					total_net_profit_percent += d.net_profit_percent
					total_net_profit_amount += d.net_profit_amount
					total_gross_profit_percent += d.gross_profit_percent
					total_gross_profit_amount += d.gross_profit_amount
				}
			})
			total_overhead = (total_amount_as_overhead / total_cost) * 100
			contigency_percent = (contigency / total_cost) * 100
			engineering_overhead = (total_amount_as_engineering_overhead / total_cost) * 100
			total_overheads = total_amount_as_overhead + total_amount_of_profit + contigency + total_amount_as_engineering_overhead
			// total_bidding_price = total_bidding_price + total_business_promotion

			frm.set_value("total_amount_as_overhead", total_amount_as_overhead)
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
			frm.set_value("total_overheads", total_overheads)
			frm.set_value("total_business_promotion", total_business_promotion)
			frm.set_value("total_bidding_price", total_bidding_price)
		}
	},
	total_design_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.design_calculation, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_design_calculation", amount)
		}
		else {
			frm.set_value("total_design_calculation", 0)
		}
	},
	total_material_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.materials, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_material_calculation", amount)
		}
		else {
			frm.set_value("total_material_calculation", 0)
		}
	},

	total_finishing_work_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.finishing_work, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_finishing_work_calculation", amount)
		}
		else {
			frm.set_value("total_finishing_work_calculation", 0)
		}
	},

	total_bolts_accessories_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.bolts_accessories, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_bolts_accessories_calculation", amount)
		}
		else {
			frm.set_value("total_bolts_accessories_calculation", 0)
		}
	},

	total_installation_cost_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.installation, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_installation_cost", amount)
		}
		else {
			frm.set_value("total_installation_cost", 0)
		}
	},

	total_heavy_equipments_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.heavy_equipments, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_heavy_equipments_calculation", amount)
		}
		else {
			frm.set_value("total_heavy_equipments_calculation", 0)
		}
	},

	total_transportation_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.transportation, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_transportation_calculation", amount)
		}
		else {
			frm.set_value("total_transportation_calculation", 0)
		}
	},
	total_manpower_subcontract_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.manpower_subcontract, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_manpower_subcontract_calculation", amount)
		}
		else {
			frm.set_value("total_manpower_subcontract_calculation", 0)
		}
	},
	total_manpower_cost_calculation: function (frm) {
		var amount = 0
		$.each(frm.doc.manpower, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("total_manpower_cost", amount)
		}
		else {
			frm.set_value("total_manpower_cost", 0)
		}
	},
})

frappe.ui.form.on('CE Master Scope of Work', {
	view(frm, cdt, cdn) {
		var child = locals[cdt][cdn]
		frappe.db.get_value('CE SOW', { 'cost_estimation': frm.doc.name, 'msow': child.msow, 'ssow': '' }, 'name')
			.then(r => {
				frappe.route_options = {
					'cost_estimation': frm.doc.name,
					'msow': child.msow,
					'qty': child.qty,
					'uom': child.unit,
				}
				frappe.set_route('Form', 'CE SOW', r.message.name)

			})

	},
	estimate(frm, cdt, cdn) {
		frm.save()
		var child = locals[cdt][cdn]

		frappe.db.get_value('CE SOW', { 'cost_estimation': frm.doc.name, 'msow': child.msow, 'ssow': '' }, 'name')
			.then(r => {
				if (r.message && Object.entries(r.message).length === 0) {
					frappe.route_options = {
						'cost_estimation': frm.doc.name,
						'company': frm.doc.company,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
					}
					frappe.new_doc('CE SOW')
				}
				else {
					frappe.route_options = {
						'cost_estimation': frm.doc.name,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
					}
					frappe.set_route('Form', 'CE SOW', r.message.name)
				}
			})

	}
})

frappe.ui.form.on('CE DESIGN CALCULATION', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('design_calculation')
		frm.trigger("total_design_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('design_calculation')
		frm.trigger("total_design_calculation")
	},
	design_calculation_remove(frm, cdt, cdn) {
		frm.trigger('total_design_calculation')
	},
})

frappe.ui.form.on('CE MATERIALS', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('materials')
		frm.trigger("total_material_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('materials')
		frm.trigger("total_material_calculation")
	},
	materials_remove(frm, cdt, cdn) {
		frm.trigger('total_material_calculation')
	},
})

frappe.ui.form.on('CE FINISHING WORK', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('finishing_work')
		frm.trigger("total_finishing_work_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('finishing_work')
		frm.trigger("total_finishing_work_calculation")
	},
	finishing_work_remove(frm, cdt, cdn) {
		frm.trigger('total_finishing_work_calculation')
	},
})

frappe.ui.form.on('CE BOLTS ACCESSORIES', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('bolts_accessories')
		frm.trigger("total_bolts_accessories_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('bolts_accessories')
		frm.trigger("total_bolts_accessories_calculation")
	},
	bolts_accessories_remove(frm, cdt, cdn) {
		frm.trigger('total_bolts_accessories_calculation')
	},
})

frappe.ui.form.on('CE FABRICATION INSTALLATION', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('installation')
		frm.trigger("total_installation_cost")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('installation')
		frm.trigger("total_installation_cost")
	},
	installation_remove(frm, cdt, cdn) {
		frm.trigger('total_installation_cost')
	},
})

frappe.ui.form.on('CE INSTALLATION MANPOWER', {
	total_workers: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_cost_calculation")
	},
	working_hours: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_cost_calculation")
	},
	days: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_cost_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_cost_calculation")
	},
	manpower_remove(frm, cdt, cdn) {
		frm.trigger('total_manpower_cost_calculation')
	}
})

frappe.ui.form.on('CE HEAVY EQUIPMENTS', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('heavy_equipments')
		frm.trigger("total_heavy_equipments_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('heavy_equipments')
		frm.trigger("total_heavy_equipments_calculation")
	},
	heavy_equipments_remove(frm, cdt, cdn) {
		frm.trigger('total_heavy_equipments_calculation')
	},
})

frappe.ui.form.on('CE TRANSPORTATION', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('transportation')
		frm.trigger("total_transportation_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('transportation')
		frm.trigger("total_transportation_calculation")
	},
	transportation_remove(frm, cdt, cdn) {
		frm.trigger('total_transportation_calculation')
	},
})

frappe.ui.form.on('CE MANPOWER SUBCONTRACT', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('manpower_subcontract')
		frm.trigger("total_manpower_subcontract_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		frm.refresh_field('manpower_subcontract')
		frm.trigger("total_manpower_subcontract_calculation")
	},
	manpower_subcontract_remove(frm, cdt, cdn) {
		frm.trigger('total_manpower_subcontract_calculation')
	},
})

frappe.ui.form.on('CE Scope of Work', {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.basic_rate
		frm.refresh_field('scope_of_work')
	},
	basic_rate: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.basic_rate
		frm.refresh_field('scope_of_work')
	}
})
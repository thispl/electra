frappe.ui.form.on('Project Budget', {
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
			frm.trigger("get_ce_data")
		}
	},
	onload(frm) {
		if (frm.doc.docstatus != 1) {
			frm.trigger("get_ce_data")
		}
	},
	get_ce_data(frm) {
			if (frm.doc.cost_estimation) {
				frappe.call({
					method: "frappe.client.get",
					args: {
						doctype: "Cost Estimation",
						filters: {
							"name": frm.doc.cost_estimation
						},
						fields: ["*"]
					},
					callback: function (r) {
						if (r.message) {
							frm.clear_table("master_scope_of_work")
							$.each(r.message.master_scope_of_work, function (i, d) {
								frm.add_child("master_scope_of_work", {
									'msow': d.msow,
									'msow_desc': d.msow_desc,
									'total_cost': d.total_cost,
									'total_overheads': d.total_overheads,
									'total_business_promotion': d.total_business_promotion,
									'total_bidding_price': d.total_bidding_price,
									'qty': d.qty,
									'unit': d.unit,
									'unit_price': d.unit_price
								})
								frm.refresh_field('master_scope_of_work')
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
													frm.clear_table('design')
													frm.clear_table('materials')
													frm.clear_table('mep_materials')
													frm.clear_table('finishing_work')
													frm.clear_table('bolts_accessories')
													frm.clear_table('installation')
													frm.clear_table('manpower')
													frm.clear_table('heavy_equipments')
													frm.clear_table('others')

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
															'amount': c.amount
														})
													})
													frm.refresh_field('design')

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
															'amount_with_overheads': c.amount_with_overheads,
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
							})
						}
					}
				});
			}
		
	},

	refresh(frm) {

		if (frm.doc.docstatus == 0) {
			frm.add_custom_button(__('Sales Order'),
				function () {
					frappe.model.open_mapped_doc({
						method: "electra.custom.make_project_so",
						frm: cur_frm
					})
				}, __('Create'));
		}
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
		frm.set_value("date_of_budget", frappe.datetime.nowdate())
	},
	validate(frm) {
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
						d.total_bidding_price = k.total_bidding_price
						d.unit_price = k.unit_price
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
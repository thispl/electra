frappe.ui.form.on('Project Budget', {
	refresh(frm) {
		if (!frm.doc.__islocal) {
			// frm.trigger("get_pb_sow")
		}
		if (frm.doc.company) {
			frm.trigger("set_series")
		}
		// frm.set_value("date_of_budget", frappe.datetime.nowdate())
		if (frm.doc.docstatus != 1) {
			frm.add_custom_button(__('Get SoW Items'),
				function () {
					frm.trigger("get_pb_sow")

				})
		}
	},
	onload(frm) {
		if (frm.doc.__islocal) {
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
							d.net_profit_percent = k.net_profit_percent
							d.net_profit_amount = k.net_profit_amount
							d.gross_profit_percent = k.gross_profit_percent //
							d.gross_profit_amount = k.gross_profit_amount // 
							d.contigency_percent = k.contigency_percent //
							d.contigency = k.contigency_amount //
							d.engineering_overhead = k.engineering_overhead_percent //
							d.total_amount_as_engineering_overhead = k.engineering_overhead_amount //
							d.total_overheads = k.overhead_amount + k.contigency_amount + k.engineering_overhead_amount
							d.total_business_promotion = k.business_promotion_amount
							d.total_cost = k.total_cost
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
					'cost_estimation': frm.doc.cost_estimation,
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
						}
					})
				})
			}
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
		var total_net_profit_amount = 0
		var total_net_profit_percent = 0
		var total_gross_profit_percent = 0
		var total_gross_profit_amount = 0
		if (frm.doc.master_scope_of_work) {
			// frm.trigger("get_pb_msow")
			$.each(frm.doc.master_scope_of_work, function (i, d) {
				total_amount_as_overhead += d.total_amount_as_overhead
				contigency += d.contigency_percent
				total_amount_as_engineering_overhead += d.total_amount_as_engineering_overhead
				// total_overheads += d.total_overheads
				total_business_promotion += d.total_business_promotion
				total_cost += d.total_cost
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
			// frm.set_value("total_overheads", total_overheads)
			// frm.set_value("total_business_promotion", total_business_promotion)
			frm.set_value("total_bidding_price", total_bidding_price)
		}

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
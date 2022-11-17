// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('CE SOW', {
	add_sub(frm) {
		if (frm.doc.add_sub) {
			frm.set_df_property("applicable_sections", "hidden", 1)
		}
		else {
			frm.set_df_property("applicable_sections", "hidden", 0)
		}

	},
	business_promotion_amount(frm){
		var business_promotion_percent = (frm.doc.business_promotion_amount / frm.doc.total_cost) * 100
		frm.set_value("business_promotion_percent",business_promotion_percent)
	},
	business_promotion_percent(frm){
		var business_promotion_amount = frm.doc.total_cost * (frm.doc.business_promotion_percent / 100)
		frm.set_value("business_promotion_amount",business_promotion_amount)
	},
	net_profit_amount(frm){
		var net_profit_percent = (frm.doc.net_profit_amount/frm.doc.total_cost) * 100
		frm.set_value("net_profit_percent",net_profit_percent)
	},
	net_profit_percent(frm){
		var net_profit_amount = frm.doc.total_cost * (frm.doc.net_profit_percent / 100)
		frm.set_value("net_profit_amount",net_profit_amount)
	},
	
	
	
	onload(frm) {
		frappe.call({
			'method': 'frappe.client.get_value',
			args: {
				'doctype': 'Cost Estimation',
				'filters': {
					'name': frm.doc.cost_estimation
				},
				'fieldname': ['docstatus']
			},
			callback: function (data) {
				if (data.message.docstatus) {
					frm.disable_save()
				}
			}
		});
		frm.trigger("add_sub")
		if (frm.doc.add_sub) {
			$.each(frm.doc.sub_scope_of_work, function (i, d) {
				frappe.call({
					method: "frappe.client.get_list",
					args: {
						'doctype': 'CE SSOW',
						filters: {
							'cost_estimation': frm.doc.cost_estimation,
							'msow': d.msow,
							'ssow': d.ssow,
							'ce_msow_id': frm.doc.name
						},
						fields: ['*']
					},
					callback(r) {
						$.each(r.message, function (j, k) {
							d.total_overhead = k.total_overhead
							d.total_amount_as_overhead = k.total_amount_as_overhead
							d.total_profit = k.total_profit
							d.total_amount_of_profit = k.total_amount_of_profit
							d.contigency_percent = k.contigency_percent
							d.contigency = k.contigency
							d.business_promotion = k.business_promotion
							d.engineering_overhead = k.engineering_overhead
							d.total_amount_as_engineering_overhead = k.total_amount_as_engineering_overhead
							d.total_cost = k.total_cost
							d.total_bidding_price = k.total_bidding_price
						})

					}
				})
				frm.refresh_field("sub_scope_of_work")
			})
		}
	},
	setup: function (frm) {
		// 	if(frm.doc.add_sub){
		frm.set_query("item", "installation", function (doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Item', 'item_group', '=', 'Installation']
				]
			};
		});

		// 	frm.set_query("ssow", "design_calculation", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "materials", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "finishing_work", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "bolts_accessories", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "installation_cost", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "heavy_equipments", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "manpower_subcontract", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});

		// 	frm.set_query("ssow", "manpower_cost", function (doc, cdt, cdn) {
		// 		let d = locals[cdt][cdn];
		// 		return {
		// 			filters: [
		// 				['Sub Scope of Work', 'master_scope_of_work', '=', d.msow]
		// 			]
		// 		};
		// 	});
		// }
	},
	refresh: function (frm) {
		frm.trigger("get_html_view")
		frm.add_custom_button(__('Back'),
			function () {
				window.location.href = "/app/cost-estimation/" + frm.doc.cost_estimation;
			});

	},
	get_html_view(frm) {
		// design
		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.design_amount_with_overheads - frm.doc.design_cost
			var profit_percent = (frm.doc.design_cost / frm.doc.design_amount_with_overheads) * 100
			var design_amount = frm.doc.design_cost
		} else {
			var profit_amount = frm.doc.design_amount_with_overheads - frm.doc.design_amount
			var profit_percent = (profit_amount / frm.doc.design_amount_with_overheads) * 100
			var design_amount = frm.doc.design_amount
		}
		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(design_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.design_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("design_html").$wrapper.html(table);

		// Materials

		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var table = `<table border='1' style="width:100%">
						<tr><th style="background-color:grey;color:white">Cost Amount</th><th  style="background-color:grey;color:white">Transfer Amount</th><th  style="background-color:grey;color:white">Transfer Cost Amount</th><th  style="background-color:grey;color:white">Selling Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
						<tr><td style="text-align:center"> QR ${Math.round(frm.doc.cost_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.transfer_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.transfer_cost_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.selling_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.profit_amount)}</td><td style="text-align:center">${Math.round(frm.doc.profit_percent)} %</td></tr>
					 </table>`
			frm.get_field("mep_materials_html").$wrapper.html(table);
		} else {

			var profit_amount = Math.round(frm.doc.materials_amount_with_overheads - frm.doc.materials_amount)
			var profit_percent = Math.round((profit_amount / frm.doc.materials_amount_with_overheads) * 100)

			var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(frm.doc.materials_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.materials_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
			frm.get_field("materials_html").$wrapper.html(table);
		}

		// Finishing Work
		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.finishing_work_amount_with_overheads - frm.doc.finishing_work_cost
			var profit_percent = (frm.doc.finishing_work_cost / frm.doc.finishing_work_amount_with_overheads) * 100
			var finishing_work_amount = frm.doc.finishing_work_cost
		} else {
			var profit_amount = frm.doc.finishing_work_amount_with_overheads - frm.doc.finishing_work_amount
			var profit_percent = (profit_amount / frm.doc.finishing_work_amount_with_overheads) * 100
			var finishing_work_amount = frm.doc.finishing_work_amount
		}
		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(finishing_work_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.finishing_work_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("finishing_work_html").$wrapper.html(table);

		// Accessories

		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.accessories_amount_with_overheads - frm.doc.accessories_cost
			var profit_percent = (frm.doc.accessories_cost / frm.doc.accessories_amount_with_overheads) * 100
			var accessories_amount = frm.doc.accessories_cost
		} else {
			var profit_amount = frm.doc.accessories_amount_with_overheads - frm.doc.accessories_amount
			var profit_percent = (profit_amount / frm.doc.accessories_amount_with_overheads) * 100
			var accessories_amount = frm.doc.accessories_amount
		}

		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(accessories_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.accessories_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("accessories_html").$wrapper.html(table);

		// Installation

		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.installation_amount_with_overheads - frm.doc.installation_amount
			var profit_percent = (frm.doc.installation_amount / frm.doc.installation_amount_with_overheads) * 100
			var installation_amount = frm.doc.installation_amount
		} else {
			var profit_amount = frm.doc.installation_amount_with_overheads - frm.doc.installation_amount
			var profit_percent = (profit_amount / frm.doc.installation_amount_with_overheads) * 100
			var installation_amount = frm.doc.installation_amount
		}

		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(installation_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.installation_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("installation_html").$wrapper.html(table);

		//Manpower
		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.manpower_amount_with_overheads - frm.doc.manpower_cost
			var profit_percent = (frm.doc.manpower_cost / frm.doc.manpower_amount_with_overheads) * 100
			var manpower_amount = frm.doc.manpower_cost
		} else {
			var profit_amount = frm.doc.manpower_amount_with_overheads - frm.doc.manpower_amount
			var profit_percent = (profit_amount / frm.doc.manpower_amount_with_overheads) * 100
			var manpower_amount = frm.doc.manpower_amount
		}

		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(manpower_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.manpower_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("manpower_html").$wrapper.html(table);

		// Heavy Equipments

		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.heavy_equipments_amount_with_overheads - frm.doc.heavy_equipments_cost
			var profit_percent = (frm.doc.heavy_equipments_cost / frm.doc.heavy_equipments_amount_with_overheads) * 100
			var heavy_equipments_amount = frm.doc.heavy_equipments_cost
		} else {
			var profit_amount = frm.doc.heavy_equipments_amount_with_overheads - frm.doc.heavy_equipments_amount
			var profit_percent = (profit_amount / frm.doc.heavy_equipments_amount_with_overheads) * 100
			var heavy_equipments_amount = frm.doc.heavy_equipments_amount
		}

		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(heavy_equipments_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.heavy_equipments_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("heavy_equipments_html").$wrapper.html(table);

		// Others

		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			var profit_amount = frm.doc.others_amount_with_overheads - frm.doc.others_cost
			var profit_percent = (frm.doc.others_cost / frm.doc.others_amount_with_overheads) * 100
			var others_amount = frm.doc.others_cost
		} else {
			var profit_amount = frm.doc.others_amount_with_overheads - frm.doc.others_amount
			var profit_percent = (profit_amount / frm.doc.others_amount_with_overheads) * 100
			var others_amount = frm.doc.others_amount
		}

		var table = `<table border='1' style="width:100%">
							<tr><th style="background-color:grey;color:white">Est.Cost Amount</th><th  style="background-color:grey;color:white">Selling Price Amount</th><th  style="background-color:grey;color:white">Profit Amount</th><th  style="background-color:grey;color:white">Profit %</th></tr>
							<tr><td style="text-align:center"> QR ${Math.round(others_amount)}</td><td style="text-align:center">QR ${Math.round(frm.doc.others_amount_with_overheads)}</td><td style="text-align:center">QR ${Math.round(profit_amount)}</td><td style="text-align:center">${Math.round(profit_percent)} %</td></tr>
						 </table>`
		frm.get_field("others_html").$wrapper.html(table);
	},
	materials_row(frm) {
		frm.trigger("total_material_calculation")
	},
	validate: function (frm) {
		frm.trigger("get_html_view")
		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.design, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Design Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("design_cost", cost_amount)
		frm.set_value("design_amount", amount)
		frm.set_value("design_amount_with_overheads", amount_with_overheads)
		frm.set_value("design_profit", profit)

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		if (frm.doc.company == 'MEP DIVISION - ELECTRA') {
			// $.each(frm.doc.mep_materials, function (i, d) {
			// 	amount += d.amount
			// 	cost_amount += d.cost_amount
			// 	if (d.unit_price < d.cost){
			// 		frappe.throw('Bidding Price should not be less than Cost Price in Materials Section')
			// 	}
			// })
			var profit = amount_with_overheads - cost_amount
			// frm.set_value("materials_cost", amount)
			// frm.set_value("materials_profit", profit)

			var cost_amount1 = 0
			var transfer_amount = 0
			var transfer_cost_amount = 0
			var selling_amount = 0
			var profit_percent = 0
			var profit_amount = 0

			$.each(frm.doc.mep_materials, function (i, d) {
				cost_amount1 += d.cost_with_transfer_percent
				transfer_amount += d.transfer_amount
				transfer_cost_amount += d.transfer_cost_amount
				selling_amount += d.amount
				// if (d.unit_price < d.cost){
				// 	frappe.throw('Bidding Price should not be less than Cost Price in Materials Section')
				// }
			})
			profit_amount = selling_amount - transfer_cost_amount
			profit_percent = Math.round((profit_amount / selling_amount) * 100)

			frm.set_value("materials_profit", profit_amount)
			frm.set_value("materials_amount", transfer_cost_amount)
			frm.set_value("materials_amount_with_overheads", selling_amount)
			frm.set_value("materials_cost", transfer_cost_amount)

			frm.set_value("cost_amount", cost_amount1)
			frm.set_value("transfer_amount", transfer_amount)
			frm.set_value("transfer_cost_amount", transfer_cost_amount)
			frm.set_value("selling_amount", selling_amount)
			frm.set_value("profit_percent", profit_percent)
			frm.set_value("profit_amount", profit_amount)


		}
		else {
			var amount = 0
			var cost_amount = 0
			var amount_with_overheads = 0
			$.each(frm.doc.materials, function (i, d) {
				amount += d.amount
				cost_amount += d.cost_amount
				amount_with_overheads += d.amount_with_overheads
				// if (d.unit_price < d.cost){
				// 	frappe.throw('Bidding Price should not be less than Cost Price in Materials Section')
				// }
			})
			var profit = amount_with_overheads - amount
			frm.set_value("materials_profit", profit)
			frm.set_value("materials_amount", amount)
			frm.set_value("materials_amount_with_overheads", amount_with_overheads)
			frm.set_value("materials_cost", cost_amount)

		}

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.finishing_work, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Finishing Work Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("finishing_work_profit", profit)
		frm.set_value("finishing_work_cost", cost_amount)
		frm.set_value("finishing_work_amount", amount)
		frm.set_value("finishing_work_amount_with_overheads", amount_with_overheads)

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.bolts_accessories, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Accessories Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("accessories_profit", profit)
		frm.set_value("accessories_cost", cost_amount)
		frm.set_value("accessories_amount", amount)
		frm.set_value("accessories_amount_with_overheads", amount_with_overheads)


		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.installation, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Installation Section')
			// }
		})
		
		var profit = amount_with_overheads - amount
		frm.set_value("installation_profit", profit)
		frm.set_value("installation_cost", cost_amount)
		frm.set_value("installation_amount", amount)
		frm.set_value("installation_amount_with_overheads", amount_with_overheads)

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.manpower, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Mapower Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("manpower_profit", profit)
		frm.set_value("manpower_cost", cost_amount)
		frm.set_value("manpower_amount", amount)
		frm.set_value("manpower_amount_with_overheads", amount_with_overheads)

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.heavy_equipments, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Tools/Equipments/Transport/Others Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("heavy_equipments_profit", profit)
		frm.set_value("heavy_equipments_cost", cost_amount)
		frm.set_value("heavy_equipments_amount", amount)
		frm.set_value("heavy_equipments_amount_with_overheads", amount_with_overheads)

		var amount = 0
		var cost_amount = 0
		var amount_with_overheads = 0
		$.each(frm.doc.others, function (i, d) {
			amount += d.amount
			cost_amount += d.cost_amount
			amount_with_overheads += d.amount_with_overheads
			// if (d.unit_price < d.cost){
			// 	frappe.throw('Bidding Price should not be less than Cost Price in Subcontract Section')
			// }
		})
		var profit = amount_with_overheads - amount
		frm.set_value("others_profit", profit)
		frm.set_value("others_cost", cost_amount)
		frm.set_value("others_amount", amount)
		frm.set_value("others_amount_with_overheads", amount_with_overheads)

		var total_bidding_price = 0
		var total_amount_as_overhead = 0
		var total_amount_as_engineering_overhead = 0
		var contigency = 0
		var total_cost = 0
		var total_overhead_percent = 0
		var net_profit_amount = 0
		var business_promotion_percent = 0
		var business_promotion_amount = 0
		var gross_profit_percent = 0
		var gross_profit_amount = 0
		var contigency_percent = 0
		var engineering_overhead_percent = 0
		var total_overheads = 0
		var total_business_promotion = 0

		var mep_net_profit_amount = 0
		var mep_net_profit_percent = 0

		
		// if (frm.doc.company == "MEP DIVISION - ELECTRA") {
		// var total_cost = frm.doc.design_cost + frm.doc.materials_cost + frm.doc.finishing_work_cost + frm.doc.accessories_cost + frm.doc.installation_amount + frm.doc.manpower_cost + frm.doc.heavy_equipments_cost + frm.doc.others_cost
		// }
		// else{
		var total_cost = frm.doc.design_amount + frm.doc.materials_amount + frm.doc.finishing_work_amount + frm.doc.accessories_amount + frm.doc.installation_amount + frm.doc.manpower_amount + frm.doc.heavy_equipments_amount + frm.doc.others_amount

		// } 
		var total_amount_as_overhead = total_cost * (frm.doc.total_overhead / 100)
		var total_amount_as_engineering_overhead = total_cost * (frm.doc.engineering_overhead / 100)
		var total_contigency = total_cost * (frm.doc.contigency_percent / 100)
		var business_promotion_amount = total_cost * (frm.doc.business_promotion_percent / 100)
		



		if (frm.doc.company == "MEP DIVISION - ELECTRA") {
			mep_net_profit_amount = frm.doc.gross_profit_amount-(frm.doc.total_amount_as_overhead + frm.doc.business_promotion_amount + frm.doc.contigency + frm.doc.total_amount_as_engineering_overhead)
			mep_net_profit_percent = (mep_net_profit_amount / total_cost) * 100
			frm.set_value('mep_net_profit_percent',mep_net_profit_percent)
		}		
		



		total_overhead_percent = (total_amount_as_overhead / total_cost) * 100
		contigency_percent = (total_contigency / total_cost) * 100
		engineering_overhead_percent = (total_amount_as_engineering_overhead / total_cost) * 100
		business_promotion_percent = (business_promotion_amount / total_cost) * 100
		
		var total_overheads = total_amount_as_overhead + total_amount_as_engineering_overhead + total_contigency + business_promotion_amount
		
		if (frm.doc.company == "MEP DIVISION - ELECTRA") {
		var gross_profit_amount = frm.doc.design_profit + frm.doc.materials_profit + frm.doc.finishing_work_profit + frm.doc.accessories_profit + frm.doc.installation_profit + frm.doc.manpower_profit + frm.doc.heavy_equipments_profit + frm.doc.others_profit	
		var total_bidding_price = total_cost + mep_net_profit_amount + total_overheads
		}
		else{
		
		var gross_profit_amount = frm.doc.design_profit + frm.doc.materials_profit + frm.doc.finishing_work_profit + frm.doc.accessories_profit + frm.doc.installation_profit + frm.doc.manpower_profit + frm.doc.heavy_equipments_profit + frm.doc.others_profit	
		var total_bidding_price = total_cost + total_overheads + frm.doc.net_profit_amount
		}
		var gross_profit_percent = (gross_profit_amount / total_bidding_price) * 100
		// var gross_profit_amount = frm.doc.total_amount_as_overhead + net_profit_amount
		// var gross_profit_amount = total_overheads + net_profit_amount
		// var net_profit_amount = frm.doc.gross_profit_amount - frm.doc.total_overheads
		

		frm.set_value("gross_profit_amount", gross_profit_amount)
		frm.set_value("gross_profit_percent", gross_profit_percent)
		frm.set_value("mep_net_profit_amount", mep_net_profit_amount)
		frm.set_value("mep_net_profit_percent", mep_net_profit_percent)



		// if (frm.doc.add_sub) {
		// 	$.each(frm.doc.sub_scope_of_work, function (i, d) {
		// 		total_amount_as_overhead += d.total_amount_as_overhead
		// 		total_amount_of_profit += d.total_amount_of_profit
		// 		total_contigency += d.contigency
		// 		total_amount_as_engineering_overhead += d.total_amount_as_engineering_overhead
		// 		total_business_promotion += d.business_promotion
		// 		total_cost += d.total_cost
		// 		total_bidding_price += d.total_bidding_price
		// 	})
		// }

		

		frm.set_value("total_amount_as_overhead", total_amount_as_overhead)
		frm.set_value("total_amount_as_engineering_overhead", total_amount_as_engineering_overhead)
		// frm.set_value("business_promotion_amount", business_promotion_amount)
		frm.set_value("contigency", total_contigency)

		frm.set_value("total_overhead", total_overhead_percent)
		frm.set_value("contigency_percent", contigency_percent)
		frm.set_value("engineering_overhead", engineering_overhead_percent)
		// frm.set_value("business_promotion_percent", business_promotion_percent)

		frm.set_value("total_cost", total_cost)
		frm.set_value("total_overheads", total_overheads)
		frm.set_value("total_bidding_price", total_bidding_price)

		

		var unit_price = (total_bidding_price / frm.doc.qty)
		frm.set_value("unit_price", unit_price)

		var total_additions = frm.doc.total_overheads + frm.doc.net_profit_amount

		// calculating selling price with Overheads distributed to all items
		if (frm.doc.company != "MEP DIVISION - ELECTRA") {
			var total_spa = 0
			$.each(frm.doc.design, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.mep_materials, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.materials, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.finishing_work, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.bolts_accessories, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.installation, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.manpower, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.heavy_equipments, function (i, d) {
				total_spa += d.amount
			})
			$.each(frm.doc.others, function (i, d) {
				total_spa += d.amount
			})

			// design
			var dt_name = frm.doc.design
			var dt_field = "design"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// materials
			var dt_name = frm.doc.materials
			var dt_field = "materials"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// MEP materials
			var dt_name = frm.doc.mep_materials
			var dt_field = "mep_materials"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Finishing Work
			var dt_name = frm.doc.finishing_work
			var dt_field = "finishing_work"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Accessories
			var dt_name = frm.doc.bolts_accessories
			var dt_field = "bolts_accessories"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Installation
			var dt_name = frm.doc.installation
			var dt_field = "installation"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Manpower
			var dt_name = frm.doc.manpower
			var dt_field = "manpower"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Heavy Equipments
			var dt_name = frm.doc.heavy_equipments
			var dt_field = "heavy_equipments"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)

			// Manpower
			var dt_name = frm.doc.others
			var dt_field = "others"
			calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa)
		}



	}
});

function calculate_selling_price(frm, dt_name, dt_field, total_additions, total_spa) {
	$.each(dt_name, function (i, d) {
		var qty = d.qty
		var sp = d.unit_price
		var spa = d.amount
		if (dt_field == 'manpower') {
			var qty = d.total_workers
			var sp = d.unit_price * d.working_hours * d.days
			var spa = sp * qty
		}
		var sp_distribution_percent = spa / total_spa
		// console.log("total_spa=",total_spa)
		// console.log('spa',spa)
		// console.log('total_additions',total_additions)
		var proportionate_overhead = sp_distribution_percent * total_additions
		var spa_with_overhead = spa + proportionate_overhead
		var sp_with_overhead = spa_with_overhead / qty
		d.rate_with_overheads = sp_with_overhead
		d.amount_with_overheads = qty * d.rate_with_overheads
		// console.log('spa',d.amount_with_overheads)
	})
	frm.refresh_field(dt_field)
}




frappe.ui.form.on('CE Sub Scope of Work', {
	sub_scope_of_work_add: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		frm.refresh_field("items");
	},
	estimate(frm, cdt, cdn) {
		frm.save()
		var child = locals[cdt][cdn]
		frappe.db.get_value('CE SSOW', { 'cost_estimation': frm.doc.cost_estimation, 'ssow': child.ssow, 'msow': child.msow, 'ce_msow_id': frm.doc.name }, 'name')
			.then(r => {
				if (r.message && Object.entries(r.message).length === 0) {
					frappe.route_options = {
						'cost_estimation': frm.doc.cost_estimation,
						'ssow': child.ssow,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
						'company': frm.doc.company,
						'ce_msow_id': frm.doc.name
					}
					frappe.set_route('Form', 'CE SSOW', 'new-ce-ssow-1')
				}
				else {
					frappe.route_options = {
						'cost_estimation': frm.doc.cost_estimation,
						'ssow': child.ssow,
						'msow': child.msow,
						'qty': child.qty,
						'uom': child.unit,
						'company': frm.doc.company,
						'ce_msow_id': frm.doc.name
					}
					frappe.set_route('Form', 'CE SSOW', r.message.name)
				}
			})

	}
})
frappe.ui.form.on('CE Items', {
	items_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
		frm.refresh_field('bolts_accessories')
		frm.refresh_field('installation')
		frm.refresh_field('heavy_equipments')
		frm.refresh_field('others')
	},
	item: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.item){
		frappe.call({
			'method': 'frappe.client.get_value',
			args: {
				'doctype': 'Item Price',
				'filters': {
					'item_code': row.item,
					'price_list': 'Standard Selling'
				},
				'fieldname': ['price_list_rate']
			},
			callback: function (data) {
				if (data.message.price_list_rate) {
					frappe.model.set_value(cdt, cdn, 'unit_price', data.message.price_list_rate);
				}
			}
		});

		if(row.item){
		frappe.call({
			'method': 'electra.utils.get_last_valuation_rate',
			args: {
				'item_code': row.item,
			},
			callback: function (r) {
				$.each(r.message, function (i, d) {
					if (d) {
						frappe.model.set_value(cdt, cdn, 'cost', d);
					}

				})
			}
		});
	}
	}
	},
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		row.cost_amount = row.cost * row.qty
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
		frm.refresh_field('bolts_accessories')
		frm.refresh_field('installation')
		frm.refresh_field('heavy_equipments')
		frm.refresh_field('others')

	},

	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		// cur_frm.set_value('materials_cost',row.amount)
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
		frm.refresh_field('bolts_accessories')
		frm.refresh_field('installation')
		frm.refresh_field('heavy_equipments')
		frm.refresh_field('others')
	},

	rate_with_overheads: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
		row.amount_with_overheads = row.qty * row.rate_with_overheads
		// cur_frm.set_value('materials_cost',row.amount)
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
		frm.refresh_field('bolts_accessories')
		frm.refresh_field('installation')
		frm.refresh_field('heavy_equipments')
		frm.refresh_field('others')
	},
})

frappe.ui.form.on('CE MEP Materials', {
	mep_materials_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("mep_materials");
	},
	item: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.item){
		frappe.call({
			'method': 'frappe.client.get_value',
			args: {
				'doctype': 'Item Price',
				'filters': {
					'item_code': row.item,
					'price_list': 'Standard Selling'
				},
				'fieldname': ['price_list_rate']
			},
			callback: function (data) {
				if (data.message.price_list_rate) {
					frappe.model.set_value(cdt, cdn, 'unit_price', data.message.price_list_rate);
				}
			}
		});
	}
		if(row.item){
		frappe.call({
			'method': 'electra.utils.get_last_valuation_rate',
			args: {
				'item_code': row.item,
			},
			callback: function (r) {
				$.each(r.message, function (i, d) {
					frappe.model.set_value(cdt, cdn, 'vr', d);
				})
			}
		});
	}
	},
	vr_with_tr_percent: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.transfer_charges = row.vr * (row.vr_with_tr_percent / 100)
		row.transfer_amount = row.qty * row.transfer_charges
		row.cost = row.vr * (1 + row.vr_with_tr_percent / 100)
		row.cost_amount = row.cost * row.qty
		row.cost_with_transfer_percent = row.vr * row.qty
		row.transfer_cost_amount = row.qty * row.cost
		row.rate_with_overheads = row.unit_price
		row.amount_with_overheads = row.qty * row.unit_price
		frm.refresh_field('mep_materials')

	},
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.transfer_charges = row.vr * (row.vr_with_tr_percent / 100)
		row.transfer_amount = row.qty * row.transfer_charges
		row.cost = row.vr * (1 + row.vr_with_tr_percent / 100)
		row.cost_amount = row.cost * row.qty
		row.cost_with_transfer_percent = row.vr * row.qty
		row.transfer_cost_amount = row.qty * row.cost
		row.amount = row.qty * row.unit_price
		row.rate_with_overheads = row.unit_price
		row.amount_with_overheads = row.qty * row.unit_price
		frm.refresh_field('mep_materials')

	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.transfer_charges = row.vr * (row.vr_with_tr_percent / 100)
		row.transfer_amount = row.qty * row.transfer_charges
		row.cost = row.vr * (1 + row.vr_with_tr_percent / 100)
		row.cost_amount = row.cost * row.qty
		row.cost_with_transfer_percent = row.vr * row.qty
		row.transfer_cost_amount = row.qty * row.cost
		row.amount = row.qty * row.unit_price
		row.rate_with_overheads = row.unit_price
		row.amount_with_overheads = row.qty * row.unit_price
		// cur_frm.set_value('materials_cost',row.amount)
		frm.refresh_field('mep_materials')
	},
})

frappe.ui.form.on('CE Items Manpower', {
	manpower_add(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field('manpower')
	},
	worker: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.call({
			'method': 'frappe.client.get_value',
			args: {
				'doctype': 'Designation',
				'filters': {
					'name': row.worker
				},
				'fieldname': ['per_hour_cost']
			},
			callback: function (data) {
				if (data.message.per_hour_cost) {
					frappe.model.set_value(cdt, cdn, 'cost', data.message.per_hour_cost);
				}
			}
		});
	},
	total_workers: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]	
		row.cost_amount = row.total_workers * row.cost * row.working_hours * row.days
		row.rate = row.unit_price * row.working_hours * row.days
		row.amount = row.total_workers * row.rate
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	working_hours: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]	
		row.cost_amount = row.total_workers * row.cost * row.working_hours * row.days
		row.rate = row.unit_price * row.working_hours * row.days
		row.amount = row.total_workers * row.rate
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	days: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]	
		row.cost_amount = row.total_workers * row.cost * row.working_hours * row.days
		row.rate = row.unit_price * row.working_hours * row.days
		row.amount = row.total_workers * row.rate
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]	
		row.cost_amount = row.total_workers * row.cost * row.working_hours * row.days
		row.rate = row.unit_price * row.working_hours * row.days
		row.amount = row.total_workers * row.rate
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	rate_with_overheads: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn]	
		row.cost_amount = row.total_workers * row.cost * row.working_hours * row.days
		row.rate = row.unit_price * row.working_hours * row.days
		row.amount_with_overheads = row.total_workers * row.rate_with_overheads
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	manpower_cost_remove(frm, cdt, cdn) {
		frm.trigger('total_manpower_calculation')
	}
})

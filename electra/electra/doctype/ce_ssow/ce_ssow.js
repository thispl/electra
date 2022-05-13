// Copyright (c) 2022, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('CE SSOW', {
	refresh:function(frm){
		frm.add_custom_button(__('Back'),
			function () {
				window.location.href = "/app/ce-sow/"+frm.doc.ce_msow_id;
			});
	},
	
	validate: function(frm) {
		
		frm.trigger("total_finishing_work_calculation")
		frm.trigger("total_accessories_calculation")
		frm.trigger("total_installation_calculation")
		frm.trigger("total_manpower_calculation")
		frm.trigger("total_heavy_equipments_calculation")
		frm.trigger("total_others_calculation")

		var amount = 0
		$.each(frm.doc.design, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("design_cost", amount)
		}
		else {
			frm.set_value("design_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.materials, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("materials_cost", amount)
		}
		else {
			frm.set_value("materials_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.finishing_work, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("finishing_work_cost", amount)
		}
		else {
			frm.set_value("finishing_work_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.bolts_accessories, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("accessories_cost", amount)
		}
		else {
			frm.set_value("accessories_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.installation, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("installation_cost", amount)
		}
		else {
			frm.set_value("installation_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.manpower, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("manpower_cost", amount)
		}
		else {
			frm.set_value("manpower_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.heavy_equipments, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("heavy_equipments_cost", amount)
		}
		else {
			frm.set_value("heavy_equipments_cost", 0)
		}

		var amount = 0
		$.each(frm.doc.others, function (i, d) {
			amount += d.amount
		})
		if (!isNaN(amount)) {
			frm.set_value("others_cost", amount)
		}
		else {
			frm.set_value("others_cost", 0)
		}
		
		var total_cost_of_the_project = frm.doc.design_cost + frm.doc.materials_cost + frm.doc.finishing_work_cost + frm.doc.accessories_cost + frm.doc.installation_cost + frm.doc.manpower_cost + frm.doc.heavy_equipments_cost + frm.doc.others_cost
		var total_amount_as_overhead = total_cost_of_the_project * (frm.doc.total_overhead / 100)
		var total_amount_as_engineering_overhead = total_cost_of_the_project * (frm.doc.engineering_overhead / 100)
		var total_amount_of_profit = total_cost_of_the_project * (frm.doc.total_profit / 100)
		var total_contigency = total_cost_of_the_project * (frm.doc.contigency_percent / 100)
		var total_overheads = total_amount_as_overhead + total_amount_as_engineering_overhead + total_amount_of_profit + total_contigency
		var total_bidding = total_cost_of_the_project + total_overheads + frm.doc.business_promotion
		frm.set_value("total_cost", total_cost_of_the_project)
		frm.set_value("total_amount_as_overhead", total_amount_as_overhead)
		frm.set_value("total_amount_as_engineering_overhead", total_amount_as_engineering_overhead)
		frm.set_value("total_amount_of_profit", total_amount_of_profit)
		frm.set_value("contigency", total_contigency)
		frm.set_value("total_overheads", total_overheads)
		frm.set_value("total_bidding_price", total_bidding)
		
	}
});

frappe.ui.form.on('CE Items', {
	design_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("design");
	},
	materials_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("materials");
	},
	finishing_work_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("finishing_work");
	},
	bolts_accessories_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("bolts_accessories");
	},
	installation_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("installation");
	},
	heavy_equipments_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("heavy_equipments");
	},
	others_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("others");
	},


	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.unit_price
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
		frm.refresh_field('design')
		frm.refresh_field('materials')
		frm.refresh_field('finishing_work')
		frm.refresh_field('bolts_accessories')
		frm.refresh_field('installation')
		frm.refresh_field('heavy_equipments')
		frm.refresh_field('others')
	},
})

frappe.ui.form.on('CE Items Manpower', {
	manpower_add: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		row.msow = frm.doc.msow;
		row.ssow = frm.doc.ssow;
		frm.refresh_field("manpower");
	},
	total_workers: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	working_hours: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	days: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	unit_price: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.total_workers * row.unit_price * row.working_hours * row.days
		frm.refresh_field('manpower')
		frm.trigger("total_manpower_calculation")
	},
	manpower_cost_remove(frm, cdt, cdn) {
		frm.trigger('total_manpower_calculation')
	}
})

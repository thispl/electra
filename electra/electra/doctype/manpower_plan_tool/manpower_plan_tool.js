// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Manpower plan Tool', {
	submit: function (frm) {
		frm.call('create_manpower_plan')
	},

	refresh(frm) {
		frm.disable_save();
	},

	designation(frm) {
		if (frm.doc.designation) {
			frappe.call({
				method: 'electra.electra.doctype.manpower_plan_tool.manpower_plan_tool.designation_filter',
				args: {
					'designation': frm.doc.designation
				},
				callback(r) {
					frm.set_value('available_manpower', r.message)
				}
			})
		}
	},

	month(frm) {
		var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		var idx = months.indexOf(frm.doc.month)
		months.forEach((v, i) => {
			i += 1
			idx += 1
			if (idx == 12) {
				idx = 0
			}
			frm.set_df_property('month_' + i, 'label', months[idx])
			if (i == 6) {
				i = 0
			}
		})
	}


});

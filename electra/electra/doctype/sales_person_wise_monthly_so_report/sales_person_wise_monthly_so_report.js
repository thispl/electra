// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Person Wise Monthly SO Report", {
	refresh(frm) {

	},
    download: function (frm) {
        var path = "electra.electra.doctype.sales_person_wise_monthly_so_report.sales_person_wise_monthly_so_report.download"
		var args = 'year=%(year)s&sales_person=%(sales_person)s'
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				sales_person:frm.doc.sales_person,
                year:frm.doc.year,
			});
		}
    },
});

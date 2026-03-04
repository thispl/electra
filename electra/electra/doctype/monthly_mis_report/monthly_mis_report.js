// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Monthly MIS Report", {
	refresh(frm) {

	},
    download: function (frm) {
        var path = "electra.electra.doctype.monthly_mis_report.monthly_mis_report.download"
		var args = 'company=%(company)s'
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				company:frm.doc.company
			});
		}
    },
});

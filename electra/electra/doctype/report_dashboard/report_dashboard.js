// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
	// refresh: function(frm) {

	// }
	download: function (frm) {
		if (frm.doc.report == 'Salary Register') {
			var path = "electra.electra.doctype.report_dashboard.salary_register.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s'
		}
		if (frm.doc.report == 'Working Progress Report') {
			var path = "electra.electra.doctype.report_dashboard.working_progress_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s'
		}

		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				date: frm.doc.date,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				division : frm.doc.division,
				department : frm.doc.department
			});
		}
	},
});

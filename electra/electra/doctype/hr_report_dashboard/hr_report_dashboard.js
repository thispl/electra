// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("HR Report Dashboard", {
    from_date(frm){
		frappe.call({
			method: 'electra.electra.doctype.report_dashboard.report_dashboard.set_to_date',
			args: {
				frequency: "Monthly",
				start_date: frm.doc.from_date
			},
			callback: function (r) {
				console.log("HI")
				if (r.message) {
					frm.set_value('to_date', r.message.end_date);
					frm.save()
				}
			}
		});
	},
	download: function (frm) {
		if (frm.doc.report == 'Salary Register') {
			var path = "electra.electra.doctype.report_dashboard.salary_register.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s'
		}
		if (frm.doc.report == 'Monthly Salary Register Print') {
			var path = "electra.electra.doctype.report_dashboard.monthly_salary_register_print.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s&status=%(status)s&currency=%(currency)s'
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
				department : frm.doc.department,
				status :frm.doc.status,
				currency:frm.doc.currency
			});
		}
	},
});

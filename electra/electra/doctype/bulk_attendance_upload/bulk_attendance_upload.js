// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Bulk Attendance Upload', {
	// refresh: function(frm) {

	// }

	download(frm){
		var path = "electra.electra.doctype.bulk_attendance_upload.bulk_attendance_upload.download"
		var args = 'from_date=%(from_date)s&to_date=%(to_date)s'

		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,
			
			});
		}
	}
});

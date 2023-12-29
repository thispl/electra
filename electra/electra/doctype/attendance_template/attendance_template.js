// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Template', {
	get_template: function (frm) {
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s', {
            cmd: "electra.electra.doctype.attendance_template.attendance_template.get_template",
            from_date: frm.doc.from_date,
            to_date: frm.doc.to_date,
            company:frm.doc.company,
        })
	},	
    create_attendance(frm) {
        console.log("HI")
        frappe.call({
			method: "electra.electra.doctype.attendance_template.attendance_template.enqueue_create_attendance",
			args: {
				from_date : frm.doc.from_date,
                to_date : frm.doc.to_date,
                company : frm.doc.company
			},
            freeze: true,
			freeze_message: 'Creating Attendance....',
			callback: function (r) {
				if (r.message == "OK") {
					frappe.msgprint("Attendance Created Successfully,Kindly check after sometime")
				}
			}
		});
	},	
    upload(frm) {
		frappe.call({
			method: "electra.electra.doctype.attendance_template.attendance_template.enqueue_upload",
			args: {
				from_date : frm.doc.from_date,
                to_date : frm.doc.to_date,
                company : frm.doc.company,
                attach :frm.doc.attach
			},
			freeze: true,
			freeze_message: 'Updating Attendance....',
			callback: function (r) {
				if (r.message == "OK") {
					frappe.msgprint("Attendance Updated Successfully")
				}
			}
		});
	}

});

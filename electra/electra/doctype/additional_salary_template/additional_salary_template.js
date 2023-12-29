// Copyright (c) 2023, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Additional Salary Template', {
	get_template: function (frm) {
		window.location.href = repl(frappe.request.url +
			'?cmd=%(cmd)s&company=%(company)s&payroll_date=%(payroll_date)s&salary_component=%(salary_component)s', {
			cmd: "electra.electra.doctype.additional_salary_template.additional_salary_template.get_template",
			company: frm.doc.company,
			payroll_date: frm.doc.payroll_date,
			// salary_component:frm.doc.salary_component
		});
	},
	process_additional_salary(frm){
		// console.log("Hii")
		frappe.call({
			method: "electra.electra.doctype.additional_salary_template.additional_salary_template.create_additional_salary",
			args: {
				filename: frm.doc.upload,
				payroll_date: frm.doc.payroll_date,
			},
			freeze: true,
			freeze_message: 'Creating Additional Salary....',
			callback: function (r) {
				if (r.message == "OK") {
					frappe.msgprint("Additional Salary Created Successfully,Kindly check after sometime")
				}
			}
		});
	}
});

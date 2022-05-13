frappe.ui.form.on('Legal Compliance Monitor', {
	refresh(frm) {
		// your code here
	},
	validate(frm){
		frm.trigger("days_left")
		frm.trigger("last_renewal_date")
	},
	next_due(frm) {
		frm.trigger("days_left")
	},
	frequency_of_renewal_days(frm){
		frm.trigger("last_renewal_date")
	},
	last_renewal_date(frm){
		if(frm.doc.frequency_of_renewal_days > 0){
			var next_due_date = frappe.datetime.add_days(frm.doc.last_renewal_date, frm.doc.frequency_of_renewal_days);
			frm.set_value("next_due", next_due_date);
			var diff = frappe.datetime.get_diff(next_due_date, frappe.datetime.nowdate())
			frm.set_value("days_left", diff);
		}
	},
	contact_number(frm) {
		var no = String(frm.doc.contact_number)
		console.log(no.length);
		if (no.length < 10) {
			frappe.msgprint(__("Contact Number should not be 'less' or 'more' than 10 Digit"));
			frappe.validated = false;
		}
	},
	possibility_status(frm) {
		if (frm.doc.possibility_status == "Unlimited Validity") {
			frm.set_value("status", "Unlimited");
		}
		if (frm.doc.possibility_status == "Not Renewable") {
			frm.set_value("status", "Not Renewable")
		}

		if (frm.doc.possibility_status == "Renewable") {
			frm.set_value("status", "Valid")
		}
	},
	days_left(frm) {
		
		if (frm.doc.days_left <= 30) {
			console.log(frm.doc.days_left)
			frm.set_value("status", "Due for Renewal")
		}
		else{
			frm.set_value("status", "Valid")
		}
	}




})

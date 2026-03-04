// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Statement of Account Dashboard", {
	print:function(frm){
		if(frm.doc.report == "Statement of Account"){
			var print_format ="Statement of Account Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Statement of Account Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
    },
	to_date(frm){
		frm.save()
	},
	download: function (frm) {
		if (frm.doc.report == 'Statement of Account') {
			var path = "electra.electra.doctype.accounts_report_dashboard.statement_of_account.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s'
		}
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				company : frm.doc.company,
				customer : frm.doc.customer

			});
		}
	
    }
});

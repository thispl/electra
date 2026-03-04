// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Ledger Summary Report", {
	print:function(frm){
		if(frm.doc.report == "Accounts Ledger Summary Report"){
			var print_format ="Accounts Ledger Summary Report Dashboard";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Ledger Summary Report")
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
		if (frm.doc.report == 'Accounts Ledger Summary Report') {
			var path = "electra.electra.doctype.report_dashboard.accounts_ledger.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&customer=%(customer)s'
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

// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Receivable Report Dashboard", {
    print:function(frm){
		if(frm.doc.report == "Accounts Receivable Report"){
			var print_format ="Accounts Receivable";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Receivable Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
    },
	download: function (frm) {
		if (frm.doc.report == 'Accounts Receivable Report') {
			var path = "electra.electra.doctype.report_dashboard.receivable_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&project=%(project)s&so_no=%(so_no)s'
		}
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
					cmd: path,
					args: args,
					date: frm.doc.date,
					company : frm.doc.company,
					customer : frm.doc.customer,
					so_no:frm.doc.so_no,
					project:frm.doc.project
			});
		}
	}
});

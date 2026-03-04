// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Consolidated Ledger Report", {
    print:function(frm){
        var print_format ="Consolidated Ledger Report";
        var f_name = frm.doc.name
        window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
            + "doctype=" + encodeURIComponent("Consolidated Ledger Report")
            + "&name=" + encodeURIComponent(f_name)
            + "&trigger_print=1"
            + "&format=" + print_format
            + "&no_letterhead=0"
        ));
	},
    download: function (frm) {
			var path = "electra.electra.doctype.report_dashboard.consolidated_ledger_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&account=%(account)s'
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				account:frm.doc.account,
				sales_person_user:frm.doc.sales_person_user,
				company : frm.doc.company,
				customer : frm.doc.customer,
				division : frm.doc.division

			});
		}
	
    }
});

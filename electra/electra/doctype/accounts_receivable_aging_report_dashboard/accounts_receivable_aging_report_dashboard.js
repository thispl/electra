// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Receivable Aging Report Dashboard", {
	print:function(frm){
		if(frm.doc.report == "Accounts Receivable Aging Report"){
			var print_format ="Accounts Receivable Aging";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Receivable Aging Report Dashboard")
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
		if (frm.doc.report == 'Accounts Receivable Aging Report') {
				var path = "electra.electra.doctype.report_dashboard.accounts_aging.download"
				var args = 'customer=%(customer)s&company_multiselect=%(company_multiselect)s'
			}
        if (path) {
			var company_list = []
			$.each(frm.doc.company_multiselect,function(i,d){
				company_list.push(d.company)
			})
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				customer : frm.doc.customer,
				division : frm.doc.division,
				company_multiselect:company_list

			});
		}
	
    }
});

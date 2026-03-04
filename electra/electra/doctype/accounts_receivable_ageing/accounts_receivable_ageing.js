// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Accounts Receivable Ageing", {
	print:function(frm){
		if(frm.doc.report == "Accounts Receivable Aging Report"){
			var print_format ="Accounts Receivable Ageing";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Receivable Ageing")
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
				var path = "electra.electra.doctype.accounts_receivable_ageing.accounts_receivable_ageing.download"
				var args = 'customer=%(customer)s&company_multiselect=%(company_multiselect)s&name=%(name)s&company=%(company)s'
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
                name:frm.doc.name,
				division : frm.doc.division,
				company_multiselect:company_list,
				company:company_list

			});
		}
	
    }
});

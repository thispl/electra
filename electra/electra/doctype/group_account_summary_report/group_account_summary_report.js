// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Group Account Summary Report", {
	refresh(frm){
		if(frm.doc.report =="Group Summary Report"){
			frm.set_query("account",function () {
				return{
					filters:{
					"company":frm.doc.company
					}
				}
			})
		}
	},
	onload(frm) {
		frm.save()
		const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const account = urlParams.get('account')
        frm.set_value('account',account.split(':')[1])
        frm.set_value('from_date',account.split(':')[2])
        frm.set_value('to_date',account.split(':')[3])
        frm.set_value('report',account.split(':')[0])
	},
	account(frm){
		frm.save()
	},
	to_date(frm){
		frm.save()
	},
    print:function(frm){
		if(frm.doc.report == "Group Summary Report"){
			var print_format ="Group Account Summary Report";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Group Account Summary Report")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
    },
	download: function (frm) {
		if (frm.doc.report == 'Group Summary Report') {
			var path = "electra.electra.doctype.report_dashboard.group_account_summary.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&account=%(account)s&currency=%(currency)s&company=%(company)s'
		}
        if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				company : frm.doc.company,
				account:frm.doc.account,
				customer : frm.doc.customer,
				currency:frm.doc.currency,

			});
		}
	
    }
});

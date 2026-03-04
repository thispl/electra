// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Accounts Report Dashboard', {
	project(frm){
		frm.set_query("so_no",function () {
			return{
				filters:{
				"project":frm.doc.project
				}
			}
		})
	},
	report(frm){
		if(frm.doc.report =="Group Summary Report"){
			frm.set_query("account",function () {
				return{
					filters:{
					"is_group":1
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
	from_date(frm){
		frappe.call({
			method: 'electra.electra.doctype.report_dashboard.report_dashboard.set_to_date',
			args: {
				frequency: "Monthly",
				start_date: frm.doc.from_date
			},
			callback: function (r) {
				console.log("HI")
				if (r.message) {
					frm.set_value('to_date', r.message.end_date);
					frm.save()
				}
			}
		});
	},
	// download(frm){
	// 	if (frm.doc.report == 'Statement of Account') {
	// 		var path = "electra.electra.doctype.accounts_report_dashboard.statement_of_account.download"
	// 		var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&customer=%(customer)s'
	// 	}

	// 	if (path) {
	// 		window.location.href = repl(frappe.request.url +
	// 			'?cmd=%(cmd)s&%(args)s', {
	// 			cmd: path,
	// 			args: args,
	// 			from_date : frm.doc.from_date,
	// 			to_date : frm.doc.to_date,	
	// 			company : frm.doc.company,
	// 			customer : frm.doc.customer,
	// 		});
	// 	}
	// },
	print:function(frm){
		console.log(frm.doc.status)
		if(frm.doc.report == "Ledger Summary Report"){
			var print_format ="Ledger Summary Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Accounts Receivable Aging Report"){
			var print_format ="Accounts Receivable Aging Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Group Summary Report"){
			var print_format ="Group Summary Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Accounts Ledger Summary Report"){
			var print_format ="Accounts Ledger Summary Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if (frm.doc.report =="Customer Ledger Report") {
			var f_name = frm.doc.name
			var print_format ="Customer Ledger Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if (frm.doc.report =="Sales Person Wise Income Report") {
			var f_name = frm.doc.name
			var print_format ="Sales Person Wise Income Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Accounts Receivable Report"){
			var print_format ="Accounts Receivable Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if (frm.doc.report =="Receipt Report") {
			var f_name = frm.doc.name
			var print_format ="Receipt Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Statement of Account"){
			var f_name = frm.doc.name
			var print_format ="Statement of Account";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Accounts Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		
	},
	download: function (frm) {
		if (frm.doc.report == 'Statement of Account') {
			var path = "electra.electra.doctype.accounts_report_dashboard.statement_of_account.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s'
		}
		if (frm.doc.report == 'Group Summary Report') {
			var path = "electra.electra.doctype.report_dashboard.group_summary_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&account=%(account)s&currency=%(currency)s'
		}
		if (frm.doc.report == 'Customer Ledger Report') {
			var path = "electra.electra.doctype.report_dashboard.customer_ledger_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&customer=%(customer)s'
		}
		if (frm.doc.report == 'Ledger Summary Report') {
			var path = "electra.electra.doctype.report_dashboard.ledger_summary.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&account=%(account)s'
		}
		if (frm.doc.report == 'Accounts Receivable Report') {
			var path = "electra.electra.doctype.report_dashboard.receivable_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&project=%(project)s&so_no=%(so_no)s'
		}
		if (frm.doc.report == 'Accounts Receivable Aging Report') {
			var path = "electra.electra.doctype.report_dashboard.accounts_aging.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&customer=%(customer)s'
		}
		if (frm.doc.report == 'Accounts Ledger Summary Report') {
			var path = "electra.electra.doctype.report_dashboard.accounts_ledger.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&customer=%(customer)s'
		}
		if (frm.doc.report == 'Receipt Report') {
			var path = "electra.electra.doctype.report_dashboard.receipt_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s'
		}
		if (frm.doc.report == 'Sales Person Wise Income Report') {
			var path = "electra.electra.doctype.report_dashboard.sales_person_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&sales_person_user=%(sales_person_user)s&company_multiselect=%(company_multiselect)s'
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
				date: frm.doc.date,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				division : frm.doc.division,
				department : frm.doc.department,
				company : frm.doc.company,
				customer : frm.doc.customer,
				currency:frm.doc.currency,
				account:frm.doc.account,
				so_no:frm.doc.so_no,
				project:frm.doc.project,
				sales_person_user:frm.doc.sales_person_user,
				company_multiselect:company_list
			});
		}
	}
});

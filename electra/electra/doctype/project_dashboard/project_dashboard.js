// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Dashboard', {
	project(frm){
		frm.set_query("so_no",function () {
			return{
				filters:{
				"project":frm.doc.project
				}
			}
		})
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
	print:function(frm){
		console.log(frm.doc.status)
		if(frm.doc.report == "Work Order vs Material Request vs Stock Brief Report"){
			var f_name = frm.doc.project
			var print_format ="Work Order Brief Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Project")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Work Order vs Material Request vs Stock Detailed Report"){
			var f_name = frm.doc.project
			var print_format ="Work Order Detailed Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Project")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Budgeted vs Actual Report"){
			var f_name = frm.doc.project
			var print_format ="Budgeted vs Actual Report";
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Project")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
	},
	download: function (frm) {
		if (frm.doc.report == 'Working Progress Report') {
			var path = "electra.electra.doctype.report_dashboard.working_progress_report.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s'
		}

		if (path) {
			window.location.href = repl(frappe.request.url +
				'?cmd=%(cmd)s&%(args)s', {
				cmd: path,
				args: args,
				date: frm.doc.date,
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				division : frm.doc.division,
				department : frm.doc.department,
				status :frm.doc.status,
				currency:frm.doc.currency
			});
		}
	},
});

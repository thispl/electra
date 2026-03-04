// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Dashboard', {
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
	get_from_to_dates(frm){
		if(frm.doc.month && frm.doc.fiscal_year)
		frappe.call({
			"method": "electra.electra.doctype.report_dashboard.target_vs_achievement_report.get_from_to_dates",
			"args":{
				"month" : frm.doc.month,
				"fiscal_year" : frm.doc.fiscal_year
			},
			callback(r){
				// console.log(r.message)
				if(r.message){
					// console.log(r.message)
					frm.set_value('from_date', r.message[0]);
					frm.set_value('to_date', r.message[1]);
				}
			}
		})

	},
	get_year_to_dates(frm){
		if(frm.doc.month && frm.doc.fiscal_year)
		frappe.call({
			"method": "electra.electra.doctype.report_dashboard.target_vs_achievement_report.get_year_to_dates",
			"args":{
				"fiscal_year" : frm.doc.fiscal_year
			},
			callback(r){
				// console.log(r.message)
				if(r.message){
					// console.log(r.message)
					frm.set_value('january', r.message);
					// frm.set_value('january', '');
					console.log(r.message)
				}
			}
		})

	},
	month(frm){
		frm.trigger('get_from_to_dates')
		frm.trigger('get_year_to_dates')
	},
	fiscal_year(frm){
		frm.trigger('get_from_to_dates')
		frm.trigger('get_year_to_dates')
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
	// setup(frm){
	// 	frm.set_query("account", function() {
	// 		return {
	// 			"filters": {
	// 				"company": frm.doc.company,
	// 			}
	// 		}
	// 	});
	// },
	print:function(frm){
		if(frm.doc.report == "Estimated vs Actual Report"){
			var print_format ="Estimated vs Actual Report";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Project Details Report"){
			var print_format ="Project Details Report";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Employee Timesheet Summary - Employee"){
			var print_format ="Employee Timesheet Summary - Employee";
			var f_name = frm.doc.name
			// window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Employee Timesheet Summary - Project"){
			var print_format ="Employee Timesheet Summary - Project";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
		if(frm.doc.report == "Ledger Summary Report"){
			var print_format ="Ledger Summary Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
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
				+ "doctype=" + encodeURIComponent("Report Dashboard")
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
				+ "doctype=" + encodeURIComponent("Report Dashboard")
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
				+ "doctype=" + encodeURIComponent("Report Dashboard")
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
				+ "doctype=" + encodeURIComponent("Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
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
		if(frm.doc.report == "Accounts Receivable Report"){
			var print_format ="Accounts Receivable Report";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Report Dashboard")
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
		if (frm.doc.report == 'Target Vs Achievement Report') {
			var path = 'electra.electra.doctype.report_dashboard.target_vs_achievement_report.download'
			var args = 'sales_person_name=%(sales_person_name)s&fiscal_year=%(fiscal_year)s&company=%(company)s&from_date=%(from_date)s&to_date=%(to_date)s&month=%(month)s&january=%(january)s'
		}
		if (frm.doc.report == 'Salary Register') {
			var path = "electra.electra.doctype.report_dashboard.salary_register.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s'
		}
		if (frm.doc.report == 'Monthly Salary Register Print') {
			var path = "electra.electra.doctype.report_dashboard.monthly_salary_register_print.download"
			var args = 'from_date=%(from_date)s&to_date=%(to_date)s&division=%(division)s&status=%(status)s&currency=%(currency)s'
		}
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
				currency:frm.doc.currency,
				company : frm.doc.company,
				month:frm.doc.month,
				fiscal_year:frm.doc.fiscal_year,
				sales_person_name:frm.doc.sales_person_name,
			});
		}
	},
});

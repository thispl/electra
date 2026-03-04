// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Person Wise Income Report Dashboard", {
	// refresh(frm){
	// 	if(frm.doc.report =="Sales Person Wise Income Report"){
	// 		frm.set_query("account",function () {
	// 			return{
	// 				filters:{
	// 				"is_group":1
	// 				}
	// 			}
	// 		})
	// 	}
	// },
	// onload(frm) {
	// 	frm.save()
	// 	const queryString = window.location.search;
    //     const urlParams = new URLSearchParams(queryString);
    //     const account = urlParams.get('account')
    //     frm.set_value('account',account.split(':')[1])
    //     frm.set_value('from_date',account.split(':')[2])
    //     frm.set_value('to_date',account.split(':')[3])
    //     frm.set_value('report',account.split(':')[0])
	// },
	// account(frm){
	// 	frm.save()
	// },
	to_date(frm){
		frm.save()
	},
    print:function(frm){
		if(frm.doc.report == "Sales Person Wise Income Report"){
			var print_format ="Sales Person Wise Income";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Sales Person Wise Income Report Dashboard")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		}
    },
	download: function (frm) {
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
				from_date : frm.doc.from_date,
				to_date : frm.doc.to_date,	
				sales_person_user:frm.doc.sales_person_user,
				company : frm.doc.company,
				company_multiselect:company_list,
				customer : frm.doc.customer,
				// division : frm.doc.division

			});
		}
	
    }
});

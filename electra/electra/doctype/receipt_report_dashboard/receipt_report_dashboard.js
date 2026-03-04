// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Receipt Report", {
	refresh(frm){
		frm.disable_save()
	},
	print:function(frm){
			let dialog = new frappe.ui.Dialog({
			title: __('Select Company to download print'),
			fields: [
				{
					label: 'Company',
					fieldtype: 'Link',
					options: 'Company',
					reqd:1,
					fieldname: 'company',  
				},
			],
			primary_action_label: __('Print'),
			primary_action: () => {
				let values = dialog.get_values();
				if (values) {
					frappe.run_serially([
						() => { frm.set_value("company",values['company'])},
						() => frm.save(),
						() => { frm.trigger("download_print") },
					])
					
				}
				dialog.hide();
			},
		});
		dialog.show();
		
    },
	download_print(frm){
		if(frm.doc.report == "Receipt Report"){
			var print_format ="Receipt Report Dashboard";
			var f_name = frm.doc.account
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Receipt Report")
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
		let dialog = new frappe.ui.Dialog({
			title: __('Select Company to Download Report'),
			fields: [
				{
					label: 'Company',
					fieldtype: 'Link',
					options: 'Company',
					reqd:1,
					fieldname: 'company',  
				},
			],
			primary_action_label: __('Download'),
			primary_action: () => {
				let values = dialog.get_values();
				if (values) {
					if (frm.doc.report == 'Receipt Report') {
						var path = "electra.electra.doctype.report_dashboard.receipt_report.download"
						var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s'
					}
					if (path) {
						window.location.href = repl(frappe.request.url +
							'?cmd=%(cmd)s&%(args)s', {
							cmd: path,
							args: args,
							from_date : frm.doc.from_date,
							to_date : frm.doc.to_date,	
							company : values['company'],
						});
					}
				}
				dialog.hide();
			},
		});
		dialog.show();



		
    }
});

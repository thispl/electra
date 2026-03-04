// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Supplier Statement of Account", {
	print:function(frm){
			var print_format ="Supplier Statement of Account";
			var f_name = frm.doc.name
			window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
				+ "doctype=" + encodeURIComponent("Supplier Statement of Account")
				+ "&name=" + encodeURIComponent(f_name)
				+ "&trigger_print=1"
				+ "&format=" + print_format
				+ "&no_letterhead=0"
			));
		},
        download: function (frm) {
            var path = "electra.electra.doctype.supplier_statement_of_account.supplier_statement_of_account.download"
            var args = 'from_date=%(from_date)s&to_date=%(to_date)s&company=%(company)s&name=%(name)s&company_multiselect=%(company_multiselect)s'
            if (path) {
                var company_list = []
                $.each(frm.doc.company_multiselect,function(i,d){
                    company_list.push(d.company)
                })
                window.location.href = repl(frappe.request.url +
                    '?cmd=%(cmd)s&%(args)s', {
                    cmd: path,
                    args: args,
                    name:frm.doc.name,
                    from_date : frm.doc.from_date,
                    to_date : frm.doc.to_date,	
                    company : company_list,
                    customer : frm.doc.customer,
                    company_multiselect:company_list
    
                });
            }
        
        },
        company(frm){
		if (frm.doc.company == "MARAZEEM SECURITY SERVICES" || frm.doc.company == "MARAZEEM SECURITY SERVICES - SHOWROOM" || frm.doc.company == "MARAZEEM SECURITY SERVICES - HO") {
			frm.set_value('letter_head', "Marazeem with Footer Text")
		}
		if (frm.doc.company == "KINGFISHER TRADING AND CONTRACTING COMPANY" || frm.doc.company == "KINGFISHER - TRANSPORTATION" || frm.doc.company == "KINGFISHER - SHOWROOM") {
			frm.set_value('letter_head', "KINGFISHER TRADING AND CONTRACTING COMPANY")
		}
		if (frm.doc.company == "Al - Shaghairi Trading and Contracting Company W.L.L (ELECTRA)" || frm.doc.company == "ELECTRA - BARWA SHOWROOM" || frm.doc.company == "ELECTRA - ALKHOR SHOWROOM" || frm.doc.company == "ELECTRA - BINOMRAN SHOWROOM" || frm.doc.company == "ELECTRA  - NAJMA SHOWROOM" || frm.doc.company == "ELECTRICAL DIVISION - ELECTRA" || frm.doc.company == "MEP DIVISION - ELECTRA" || frm.doc.company == "STEEL DIVISION - ELECTRA" || frm.doc.company == "TRADING DIVISION - ELECTRA" || frm.doc.company == "INTERIOR DIVISION - ELECTRA" || frm.doc.company == "ENGINEERING DIVISION - ELECTRA") {
			frm.set_value('letter_head', "Electra")
		}
	},
});

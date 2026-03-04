// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Statement of Accounts Report - Project", {
    print:function(frm){
        if(frm.doc.report == "Statement of Account"){
            var print_format ="Statement of Accounts Report - Project";
            var f_name = frm.doc.name
            console.log(frm)
            window.open(frappe.urllib.get_full_url("/api/method/frappe.utils.print_format.download_pdf?"
                + "doctype=" + encodeURIComponent("Statement of Accounts Report - Project")
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
        if (frm.doc.report == 'Statement of Account') {
            var path = "electra.electra.doctype.accounts_report_dashboard.statement_of_account_project.download"
            var args = 'from_date=%(from_date)s&project=%(project)s&to_date=%(to_date)s&company=%(company)s&name=%(name)s&company_multiselect=%(company_multiselect)s'
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
                name:frm.doc.name,
                from_date : frm.doc.from_date,
                to_date : frm.doc.to_date,	
                company : company_list,
                customer : frm.doc.customer,
                company_multiselect:company_list,
                project:frm.doc.project,

            });
        }

    }
});

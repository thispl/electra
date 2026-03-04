// Copyright (c) 2025, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Progress Report", {
    onload(frm) {
        frm.trigger("set_queries");
    },

    sales_order(frm) {
        frm.trigger("set_queries");
    },

    project(frm) {
        frm.trigger("set_queries");
    },

    set_queries(frm) {
        frm.set_query("project", function () {
            return{
                filters:{
                "sales_order":frm.doc.sales_order
                }
            }
        });

        frm.set_query("sales_order", function () {
            return{
                filters:{
                "project":frm.doc.project
                }
            }
        });
    },

    download: function (frm) {
        if (frm.doc.project) {
            if (frm.doc.report == 'Project Progress Report') {
                var path = 'electra.electra.doctype.project_progress_report.project_progress_report.download'
                var args = 'project=%(project)s'
            }
            if (path) {
                    window.location.href = repl(frappe.request.url +
                        '?cmd=%(cmd)s&%(args)s', {
                        cmd: path,
                        args: args,
                        project: frm.doc.project,
                    });
            }
        }
        if (frm.doc.sales_order) {
            if (frm.doc.report == 'Project Progress Report') {
                var path = 'electra.electra.doctype.project_progress_report.project_progress_report.download'
                var args = 'sales_order=%(sales_order)s'
            }
            if (path) {
                    window.location.href = repl(frappe.request.url +
                        '?cmd=%(cmd)s&%(args)s', {
                        cmd: path,
                        args: args,
                        sales_order: frm.doc.sales_order,
                    });
            }
        }
    }
});

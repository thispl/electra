// Copyright (c) 2024, Abdulla and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Item Price List Upload Tool", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Item Price List Upload Tool", {
    get_template: function (frm) {
        console.log(frappe.request.url)
        window.location.href = repl(frappe.request.url +
            '?cmd=%(cmd)s&currency=%(currency)s', {
            cmd: "electra.electra.doctype.item_price_list_upload_tool.item_price_list_upload_tool.get_template",
            currency: frm.doc.currency,
        });
    },
    });
    
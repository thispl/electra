// // Copyright (c) 2024, Abdulla and contributors
// // For license information, please see license.txt

// frappe.ui.form.on("Advance Invoice", {
// 	before_workflow_action: async (frm) => {
// 		if (frm.doc.workflow_state == "Draft") {
// 			let promise = new Promise((resolve, reject) => {
// 				if (frm.selected_workflow_action == "Payment Pending") {
// 					frappe.call({
//                         method:"electra.custom.create_new_journal_entry",
//                         args:{
//                             name:frm.doc.name,
// 							so:frm.doc.sales_order,
// 							date:frm.doc.transaction_date,
//                         },
//                         callback(r){

//                         }

//                     })
// 				}
// 			});
// 			await promise.catch((error) => frappe.throw(error));
// 		}
// 	},
// });

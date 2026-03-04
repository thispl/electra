// frappe.listview_settings['Delivery Note WIP'] = {
// 	get_indicator: function(doc) {
// 		if(cint(doc.is_return)==1) {
// 			return [__("Return"), "gray", "is_return,=,Yes"];
// 		} else if (doc.status === "Closed") {
// 			return [__("Closed"), "green", "status,=,Closed"];
// 		} else if (doc.status === "Return Issued") {
// 			return [__("Return Issued"), "grey", "status,=,Return Issued"];
// 		} else if (flt(doc.per_billed, 2) < 100) {
// 			return [__("To Bill"), "orange", "per_billed,<,100"];
// 		} else if (flt(doc.per_billed, 2) === 100) {
// 			return [__("Completed"), "green", "per_billed,=,100"];
// 		}
// 	},
// }
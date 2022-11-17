// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vacation Final Exit Form', {
			refresh(frm) {
				// your code here
			},

			onload(frm){
				frm.trigger("get_today_date")
				frm.trigger("user_validate")
			},
			
			// get_today_date:function(frm){
			// 	var today = new Date()
			// 	console.log(today)
			// 	var dd = today.getDate();
			// 	var mm = today.getMonth() + 1; 
			// 	var yyyy = today.getFullYear();
			// 	if(dd<10) 
			// 		{
			// 			dd='0'+dd;
			// 		} 
					
			// 	if(mm<10) 
			// 		{
			// 			mm='0'+mm;
			// 		} 
			// 	today = dd+'-'+mm+'-'+yyyy;
			// 	frm.set_value('date',today)
				
			// },
			
		

	// }
	// user_validate:function(frm){
	// 	hide_field(['site_store_clearance','employee_details','admin_hr_clearance','it_clearance','finance_clearance','clearance_approval']);
	// 	if(frappe.user.has_role('Administrator')){
	// 		unhide_field(['site_store_clearance','employee_details','admin_hr_clearance','it_clearance','finance_clearance','clearance_approval'])
	// 	}
		//  if(frappe.user.has_role('Manager')){
		// 	unhide_field(['employee_details'])

		// }
		//  if(frappe.user.has_role('Manager')){
		// 	unhide_field(['admin_hr_clearance'])

		// }
		//  if(frappe.user.has_role('Manager')){
		// 	unhide_field(['it_clearance'])

		// }
		//  if(frappe.user.has_role('Manager')){
		// 	unhide_field(['finance_clearance'])

		// }
		//  if(frappe.user.has_role('Manager')){
		// 	unhide_field(['clearance_approval'])

		// }
		
	})


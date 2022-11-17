// // Copyright (c) 2022, Abdulla and contributors
// // For license information, please see license.txt

// frappe.ui.form.on('Project Day Plan', {
// 	onload(frm) {
// 		if (frm.doc.__islocal) {		
// 			frm.clear_table("project_day_plan_list")
// 			frappe.db.get_list('Project', {
// 				fields:['project_name','name'],
// 				filters: {
// 					status: 'Open'
// 				}
// 			}).then(records => {
// 				console.log(records)
// 				$.each(records, function (i, r) {
// 					frm.add_child("project_day_plan_list", {
// 						'project': r.name,
// 						'project_name':r.project_name
// 					})
// 					frm.refresh_field("project_day_plan_list")
// 				})
// 			})
// 		}
// 	},
// })
// frappe.ui.form.on('Project Day Plan List', {
// 	add_employee: function (frm, cdt, cdn) {
// 		var row = locals[cdt][cdn]

// 		let dialog = new frappe.ui.Dialog({
// 			title: __('Select Employees'),
// 			fields: [
// 				{
// 					label: 'Project Name',
// 					fieldtype: 'Link',
// 					options: 'Project',
// 					default: row.project,
// 					fieldname: 'project',
// 				},
// 				{
// 					label: 'Employee List',
// 					fieldtype: 'Table MultiSelect',
// 					options: 'Project Day Plan Employee',
// 					fieldname: 'employee',
// 				}
// 			],
// 			primary_action_label: __('Add'),
// 			primary_action: () => {
// 				let values = dialog.get_values();
// 				if (values) {
// 					var project = values['project']
// 					$.each(values['employee'], function (i, k) {
// 						frm.add_child("project_day_plan_employee", {
// 							'employee': k.employee,
// 							'project': project
// 						})
// 					})
// 					frm.refresh_field("project_day_plan_employee")

// 				}
// 			},
// 		});
// 		dialog.show();

// 	},
// })
// frappe.ui.form.on('Project Day Plan Employee', {
// 	to_time: function(frm,cdt,cdn){
// 		var row = locals[cdt][cdn]
// 		var to_time = row.to_time
// 		var from_time =row.from_time

// 		// console.log(time_end - time_start)


// 		// var value_start = from_time.split(':')
// 		// var value_end = to_time.split(':');
// 		// console.log(value_start,value_end)

// 		// var time1 = value_start[0]+value_start[1]+value_start[2];
// 		// var time2 = value_end[0]+value_end[1]+value_end[2];
// 		// var diff = time2- time1
// 		// console.log(diff)


// 		// time1 - time2;
	
// 		// var msec = diff;
// 		// var hh = Math.floor(msec / 1000 / 60 / 60);
// 		// msec -= hh * 1000 * 60 * 60;
// 		// var mm = Math.floor(msec / 1000 / 60);
// 		// msec -= mm * 1000 * 60;
// 		// var ss = Math.floor(msec / 1000);
// 		// msec -= ss * 1000;

// 		// console.log(hh + ":" + mm + ":" + ss);



// 	}
// })

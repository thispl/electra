// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Day Plan', {
	validate(frm){
		$.each(frm.doc.employee_table,function(i,d){
			// console.log(d)
			d.planned_date = frm.doc.planned_date
			// d.employee = frm.doc.employee
		})	
		

		$.each(frm.doc.employee_multiselect,function(i,d){
			d.planned_date = frm.doc.planned_date
		})
	},
	
	setup(frm) {
		frm.set_query("project", function() {
			return {
				filters: {
					'customer': frm.doc.customer
				}
			};
		});
		
	},
	onload(frm) {
	    if(frm.doc.__islocal){
		frm.set_value("planned_date",frappe.datetime.now_datetime())
		if(frm.doc.entry_type == 'In Group'){
			frm.clear_table("employee_multiselect")
		}
		else{
			frm.clear_table("employee_table")
		}
        }
	},
	// refresh(frm){
	// 	if(!frm.doc.__islocal){
	// 		frm.add_custom_button(__('Timesheet'),
	// 		function () {
	// 			frappe.model.open_mapped_doc({
	// 				method: "electra.electra.doctype.day_plan.day_plan.make_day_plan",
	// 				frm: cur_frm
	// 			})
	// 		}, __('Create'));
	// 	}
	// },

	entry_type(frm){
		frm.trigger("select_group")
	},
	company(frm){
		frm.trigger("select_group")
	},
	select_group(frm){
		if(frm.doc.entry_type == 'In Group'){
			frm.clear_table("employee_multiselect")
			frm.trigger("get_employees")
		}
		else{
			frm.clear_table("employee_table")
		}
	},
	get_employees(frm){
		frm.clear_table("employee_table")
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Employee",
				order_by: "employee_name",
				filters: {'status':'Active','company':frm.doc.company},
				fields: ["name","employee_name","designation","grade","cell_number"],
			},
			callback: function(r) {
				if(r.message) {
				    frm.clear_table("employee_table");
					$.each(r.message,function(i,d){
						frm.add_child("employee_table", {
							employee: d.name,
							employee_name : d.employee_name,
							designation : d.designation,
							grade : d.grade,
							contact_no : d.cell_number,
						})
						frm.refresh_field('employee_table');
					})
				}
			}
		});
	},
});

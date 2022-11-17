// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Day Plan Timesheet', {
	day_plan(frm){
		frm.clear_table("time_log")
		frappe.db.get_list('Day Plan Employee', {
            fields: ['*'],
            filters: {
                parent: frm.doc.day_plan
            },
            order_by: "idx",
        }).then(records => {
            $.each(records,function(i,d){
                d.employee
				frm.add_child("time_log", {
					employee: d.employee,
					employee_name : d.employee_name,
					designation : d.designation,
					grade : d.grade,
					contact_no : d.contact_no,
				})
				frm.refresh_field('time_log');
            });
        })
	},
	entry_type(frm){
		frm.trigger("select_group")
	},
	select_group(frm){
		if(frm.doc.entry_type == 'In Group'){
			frm.clear_table("time_log")
			frm.trigger("get_employees")
		}
		else{
			frm.clear_table("time_log")
			frm.refresh_field('time_log');
		}
	},
	get_employees(frm){
		frm.clear_table("time_log")
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
				    frm.clear_table("time_log");
					$.each(r.message,function(i,d){
						frm.add_child("time_log", {
							employee: d.name,
							employee_name : d.employee_name,
							designation : d.designation,
							grade : d.grade,
							contact_no : d.cell_number,
						})
						frm.refresh_field('time_log');
					})
				}
			}
		});
	},
	setup(frm){
		console.log(frm.doc.project)
		frm.set_query("activity", "time_log", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Task', 'project', '=', frm.doc.project]
				]
			};
		});
	}
});

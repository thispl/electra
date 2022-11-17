// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Staff Skill Mapping Form', {
	onload: function(frm) {
		if(frm.doc.__islocal){
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Skill Set",
					order_by: "name",
					fields: ["name"],
				},
				callback: function(r) {
					if(r.message) {
						frm.clear_table("table_14");
						$.each(r.message,function(i,d){
							frm.add_child("table_14", {
								skill_sets: d.name,
							})
							frm.refresh_field('table_14');
						})
					}
				}
			});
		}
		
	}
});

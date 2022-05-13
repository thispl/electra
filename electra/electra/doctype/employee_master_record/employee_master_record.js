// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Master Record', {
	refresh: function(frm) {
		

	},

	employee_id(frm){
		frappe.call({
    		method: "frappe.client.get_list",
    		args: {
    			doctype: "Leave Application",
    			filters: {
    				"employee": frm.doc.employee_id
    			},
				fields:['leave_type', 'from_date','to_date','ticket_required','from','to']
    		},
			callback(r){
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('leave_tracker',{
	                        'leave_type':v.leave_type,
	                        'from_date':v.from_date,
	                        'to_date':v.to_date,
	                        'air_ticket':v.ticket_required,
							'from': v.from,
							'to' : v.to
	                    })
						frm.refresh_field('leave_tracker')
					})
				}

				
			}
		})

		frappe.call({
			method :"frappe.client.get",
			args: {
				doctype: "Employee Transfer",
    			filters: {
    				name: frm.doc.employee,
    			},
				fields: ['name','transfer_date'],
			},
			callback(r){
				var transfer_date = r.message.transfer_date
				frappe.call({
					method: "electra.utils.get_transfer",
					args: {
						'employee_transfer_id' : r.message.name,
					},
					
					callback(r){
						console.log(r.message)
						if(r.message){
							
							$.each(r.message,function(i,v){
								console.log(v)
								frm.add_child('employee_transfer',{
						            'property':v.property,
									'current':v.current,
									'new':v.new,
									'transfer_date':transfer_date
						        })
								frm.refresh_field('employee_transfer')
							})
						}
		
						
					}
				})
			}
		})

		
	


		frappe.call({
    		method: "frappe.client.get_list",
    		args: {
    			doctype: "Salary Structure Assignment",
    			filters: {
    				"employee": frm.doc.employee_id
    			},
				fields:['employee_name', 'salary_structure','base','from_date']
    		},
			callback(r){
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('employee_increment',{
	                        'employee_name':v.employee_name,
	                        'salary_structure':v.salary_structure,
	                        'base':v.base,
							'date':v.from_date
	                    })
						frm.refresh_field('employee_increment')
					})
				}

				
			}
		})
	

	
		frappe.call({
    		method: "frappe.client.get_list",
    		args: {
    			doctype: "Warning Letter",
    			filters: {
    				"emp_id": frm.doc.employee_id
    			},
				fields:['warning_template']
    		},
			callback(r){
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('warning_letter',{
	                        'warning_letter':v.warning_template,
	                    })
						frm.refresh_field('warning_letter')
					})
				}

				
			}
		})
	
	}
});

// Copyright (c) 2021, Abdulla and contributors
// For license information, please see license.txt

frappe.ui.form.on('HR Dashboard', {
	refresh: function(frm) {
		frappe.call({
			method :"electra.electra.doctype.hr_dashboard.hr_dashboard.legal_compliance",
			callback(r){
				console.log(r.message)
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('legal_compliance',{
	                        'employee':v.custodian,
	                        'employee_id':v.custodian_name,
	                        'document':v.name,
	                        'renewal_date':v.next_due,
	                    })
						frm.refresh_field('legal_compliance')
					})
				}

				
			}
		})


		frappe.call({
			method :"electra.electra.doctype.hr_dashboard.hr_dashboard.visa_renewal",
			callback(r){
				// console.log(r.message)
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('visa_renewal',{
	                        'visa_application_number':v.visa_application_no,
	                        'nationality':v.nationality,
	                        'document':v.name,
	                        'expiry_date':v.visa_expiry_date,
	                    })
						frm.refresh_field('visa_renewal')
					})
				}

				
			}
		})

		frappe.call({
			method :"electra.electra.doctype.hr_dashboard.hr_dashboard.vehicle_renewal",
			callback(r){
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('vehicle_renewal',{
	                        'vehicle':v.name,
	                        'employee':v.employee,
	                        'document':v.name,
	                        'istimara_expiry':v.expiry_of_istimara,
	                    })
						frm.refresh_field('vehicle_renewal')
					})
				}

				
			}
		})
	
		frappe.call({
			method :"electra.electra.doctype.hr_dashboard.hr_dashboard.staff_arrival",
			callback(r){
				console.log(r.message)
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('staff_arrival',{
	                        'employee':v.employee_name,
							'arrival_date':v.end,
	                        
	                    })
						frm.refresh_field('staff_arrival')
					})
				}

				
			}
		})
    
		frappe.call({
			method :"electra.electra.doctype.hr_dashboard.hr_dashboard.staff_vacation",
			callback(r){
				console.log(r.message)
	            if(r.message){
					$.each(r.message,function(i,v){
						frm.add_child('staff_vacation',{
	                        'employee':v.employee_name,
							'vacation_date':v.from_date,
	                        
	                    })
						frm.refresh_field('staff_vacation')
					})
				}

				
			}
		})
	}
});

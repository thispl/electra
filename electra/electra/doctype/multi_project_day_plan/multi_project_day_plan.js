frappe.ui.form.on('Multi Project Day Plan', {
    setup(frm){
        
    },
//     on_submit(frm){
//         frm.trigger('calculation')
//     },
//     validate(frm){
//         frm.trigger('calculation')
//     },
//     calculation(frm){
//         $.each(frm.doc.project_day_plan_employee,function(i,d){
//         var to_time = d.to_time
// 		var from_time =d.from_time
// 		var lunch_break=d.lunch_break
		
// 		var time1= from_time.split(':')
// 		var time2= to_time.split(':')
// 		var time3= lunch_break.split(':')
// 		var hourInMinOfEntry=time1[0] * 60;
//     	var hourInMinOfExit = time2[0] * 60;
//     	var lunch = time3[0] * 60;
    	
//     	var secondInMinOfEntry = time1[0] / 60;
//     	var secondInMinOfExit = time2[0] / 60;
//     	var lunch_time = time3[0] / 60;
//     	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
//     	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
//     	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
//     	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
//         var num = dif;
//         // console.log(num);
//         var hours = (num / 60);
//         var rhours = Math.floor(hours);
//         var minutes = (hours - rhours) * 60;
//         var rminutes = Math.round(minutes);
//         // console.log(rhours +":"+ rminutes +":"+'00');
//         d.total_working_hours = rhours +":"+ rminutes +":"+'00'
//         if(num > 480.1333333333333){
//             var ghours = rhours - 8
//             var gminutes = rminutes - 0 
//             var ot_hours = ghours +":"+ gminutes +':00'
//             d.ot = ot_hours 
//         }
//         else{
//             d.ot = "00:00:00"
//         }
//     })
    
//     },
	onload(frm) {
		if (frm.doc.__islocal) {
		    frm.trigger('company')
		}
		
	    
    },
    company(frm){
        var company = frm.doc.company
		frappe.db.get_list('Project', {
			fields:['project_name','name'],
			filters: {
				status: 'Open',
				company
			},
		    }).then(records => {
				frm.clear_table("project_day_plan_list")
			$.each(records, function (i, r) {
				frm.add_child("project_day_plan_list", {
					'project': r.name,
					'project_name':r.project_name
				})
				frm.refresh_field("project_day_plan_list")
		})
		})
    }
})

frappe.ui.form.on('Project Day Plan List', {
    add_employee: function (frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        let dialog = new frappe.ui.Dialog({
            title: __('Select Employees'),
            fields: [
                {
                    label: 'Project',
                    fieldtype: 'Link',
                    options: 'Project',
                    default: row.project,
                    fieldname: 'project',
                },
                {
                    label: 'Project Name',
                    fieldtype: 'Data',
                    default: row.project_name,
                    fieldname: 'project_name',
                },
                {
                    label: 'Employee List',
                    fieldtype: 'Table MultiSelect',
                    ignore_user_permissions: 1,
                    options: 'Project Day Plan Child',
                    fieldname: 'employee',
                },
            ],
            primary_action_label: __('Add'),
            primary_action: function () {
                addSelectedEmployees(dialog, frm, row);
            },
        });
        dialog.show();
    },
});

var allSelectedEmployees = [];

function addSelectedEmployees(dialog, frm, row) {
    let values = dialog.get_values();

    if (values) {
        var project = values['project'];
        var project_name = values['project_name'];
    
        var selectedEmployees = [];

        function processEmployee(employee) {
            if (allSelectedEmployees.includes(employee)) {
                frappe.msgprint('Employee ' + employee + ' is already selected for another project.');
                return;
            }
            if (selectedEmployees.includes(employee)) {
                frappe.msgprint('Employee ' + employee + ' is already selected for this project.');
                return;
            }

            frappe.call({
                method: 'electra.custom.update_emp_value',
                args: {
                    employee: employee,
                },
                callback: function (r) {
                    if (r.message) {
                        var employeeName = r.message[0];
                        var designation = r.message[1];
                        var grade = r.message[2];

                        // if (!(designation === "Supervisor" || designation === "Sr. Supervisor" || grade === "NON STAFF")) {
                            frm.add_child("project_day_plan_employee", {
                                'employee': employee,
                                'project_name': project_name,
                                'employee_name': employeeName,
                                'project': project,
                                'lunch_break': '1:00'
                            });
                            frm.refresh_field("project_day_plan_employee");
                            selectedEmployees.push(employee);
                            allSelectedEmployees.push(employee);
                    //     } else {
                    //         frappe.msgprint('Employee ' + employee + ' does not meet the criteria (Supervisor or Sr. Supervisor designation, or Non Staff grade).');
                    //     }
                    // } else {
                    //     frappe.msgprint('Error fetching employee details for ' + employee);
                    }
                }
            });
        }
        $.each(values['employee'], function (i, k) {
            processEmployee(k.employee);
        });
    }

    dialog.hide();
}


frappe.ui.form.on('Project Day Plan Child', {
    employee:function(frm,cdt,cdn){
        var row = locals[cdt][cdn]
        row.employee(ignore_permissions=True)
    },
//     from_time: function(frm,cdt,cdn){
// 		var row = locals[cdt][cdn]
// 		var from_time = row.from_time
// 		var time2= from_time.split(':')
//     	var hourInMinOfExit = time2[0] * 60;
//     	var secondInMinOfExit = time2[0] / 60;
//     	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
//         var num = totalMinsOfExit
//         var hours = (num / 60);
//         var rhours = Math.floor(hours);
//         var minutes = (hours - rhours) * 60;
//         var rminutes = Math.round(minutes);
//         var ghours = rhours + 9
//         var gminutes = rminutes + 0 
//         var totime = ghours +":"+ gminutes +':00'
//         console.log(totime)
//         row.to_time = totime 
//         frm.trigger('to_time')
//         frm.refresh_field("project_day_plan_employee")
		
//     },
// 	to_time: function(frm,cdt,cdn){
// 		var row = locals[cdt][cdn]
// 		var to_time = row.to_time
// 		var from_time =row.from_time
// 		var lunch_break=row.lunch_break
		
// 		var time1= from_time.split(':')
// 		var time2= to_time.split(':')
// 		var time3= lunch_break.split(':')
// 		var hourInMinOfEntry=time1[0] * 60;
//     	var hourInMinOfExit = time2[0] * 60;
//     	var lunch = time3[0] * 60;
    	
//     	var secondInMinOfEntry = time1[0] / 60;
//     	var secondInMinOfExit = time2[0] / 60;
//     	var lunch_time = time3[0] / 60;
//     	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
//     	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
//     	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
//     	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
//         var num = dif;
//         // console.log(num);
//         var hours = (num / 60);
//         var rhours = Math.floor(hours);
//         var minutes = (hours - rhours) * 60;
//         var rminutes = Math.round(minutes);
//         // console.log(rhours +":"+ rminutes +":"+'00');
//         row.total_working_hours = rhours +":"+ rminutes +":"+'00'
//         if(num > 480.1333333333333){
//             var ghours = rhours - 8
//             var gminutes = rminutes - 0 
//             var ot_hours = ghours +":"+ gminutes +':00'
//             row.ot = ot_hours 
//         }
//         else{
//             row.ot = "00:00:00"
//         }
//         frm.refresh_field("project_day_plan_employee")
// 	},
// 	lunch_break: function(frm,cdt,cdn){
// 		var row = locals[cdt][cdn]
// 		var to_time = row.to_time
// 		var from_time =row.from_time
// 		var lunch_break=row.lunch_break
		
// 		var time1= from_time.split(':')
// 		var time2= to_time.split(':')
// 		var time3= lunch_break.split(':')
// 		var hourInMinOfEntry=time1[0] * 60;
//     	var hourInMinOfExit = time2[0] * 60;
//     	var lunch = time3[0] * 60;
    	
//     	var secondInMinOfEntry = time1[0] / 60;
//     	var secondInMinOfExit = time2[0] / 60;
//     	var lunch_time = time3[0] / 60;
//     	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
//     	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
//     	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
//     	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
//         var num = dif;
//         // console.log(num);
//         var hours = (num / 60);
//         var rhours = Math.floor(hours);
//         var minutes = (hours - rhours) * 60;
//         var rminutes = Math.round(minutes);
//         // console.log(rhours +":"+ rminutes +":"+'00');
//         row.total_working_hours = rhours +":"+ rminutes +":"+'00'
//         if(num > 480.1333333333333){
//             var ghours = rhours - 8
//             var gminutes = rminutes - 0 
//             var ot_hours = ghours +":"+ gminutes +':00'
//             row.ot = ot_hours 
//         }
//         else{
//             row.ot = "00:00:00"
//         }
//         frm.refresh_field("project_day_plan_employee")
// 	}
// 	
})

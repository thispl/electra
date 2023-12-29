frappe.ui.form.on('Projects Timesheet', {
    setup(frm){
		frm.set_query("activity", "project_day_plan_employee", function(doc, cdt, cdn) {
			let d = locals[cdt][cdn];
			return {
				filters: [
					['Task', 'project', '=', d.project]
				]
			};
		});
	},
	plan_date(frm){
		$.each(frm.doc.project_day_plan_employee,function(i,d){
			d.worked_date = frm.doc.plan_date
		})
		frm.refresh_field('project_day_plan_employee')
	},
    day_plan(frm){
		frm.clear_table("project_day_plan_employee")
		// frappe.db.get_list('Day Plan Employee', {
        //     fields: ['*'],
        //     filters: {
        //         parent: frm.doc.day_plan
        //     },
        //     order_by: "idx",
        // }).then(records => {
        //     $.each(records,function(i,d){
		// 		frm.add_child("project_day_plan_employee", {
		// 			project: d.project,
		// 			project_name: d.project_name,
		// 			employee: d.employee,
		// 			employee_name : d.employee_name,
		// 			designation : d.designation,
		// 		})
		// 		frm.refresh_field('project_day_plan_employee');
        //     });
        // })
        if(frm.doc.day_plan){
            frappe.call({
                method:"electra.custom.get_day_plan_details",
                args:{
                    "day_plan":frm.doc.day_plan,
                },
                callback(r){
                    if(r.message){
                        $.each(r.message,function(i,d){
                            frm.add_child("project_day_plan_employee", {
                                project: d.project,
                                project_name: d.project_name,
                                employee: d.employee,
                                employee_name : d.employee_name,
                                designation : d.designation,
                                worked_date:frm.doc.plan_date
                            })
                            frm.refresh_field('project_day_plan_employee');
                        });
                    }
                }
            })
        }
        
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
	onload(frm) { 
        // $.each(frm.doc.project_day_plan_employee,function(i,d){
            
        //     if(d.employee && d.total_working_hours && d.ot){
        //     frappe.call({
        //         method: "electra.custom.update_amount",
        //         args: {
        //             'employee':d.employee,
        //             'wh':d.total_working_hours,
        //             'ot':d.ot
        //         },
        //         callback: function(r) {
        //             if(r.message) {
        //                 frm.clear_table("project_day_plan_employee");
        //                 console.log(r.message)
        //             }
        //         }
        //     });
        // }

        // })
        frm.refresh_field('project_day_plan_employee')
		if(frm.doc.__islocal){
			if(frm.doc.multi_project_day_plan){
				frappe.call({
					method: "electra.custom.proj_day_plan_emp",
					args: {
						multi_project_day_plan: frm.doc.multi_project_day_plan,
					},
					callback: function(r) {
						if(r.message) {
							frm.clear_table("project_day_plan_employee");
							$.each(r.message,function(i,d){
								frm.add_child("project_day_plan_employee", {
									project: d.project,
									project_name: d.project_name,
									employee : d.employee,
                                    worked_date:frm.doc.plan_date
								})
								frm.refresh_field('project_day_plan_employee');
							})
						}
					}
				});
			}	
		}				
	},
    on_submit(frm){
        frm.trigger('calculation')
    },
    validate(frm){
        // frm.trigger('calculation')
    },
    calculation(frm){
        $.each(frm.doc.project_day_plan_employee,function(i,d){
        var to_time = d.to_time
		var from_time =d.from_time
		var lunch_break=d.lunch_break
		
		var time1= from_time.split(':')
		var time2= to_time.split(':')
		var time3= lunch_break.split(':')
		var hourInMinOfEntry=time1[0] * 60;
    	var hourInMinOfExit = time2[0] * 60;
    	var lunch = time3[0] * 60;
    	
    	var secondInMinOfEntry = time1[0] / 60;
    	var secondInMinOfExit = time2[0] / 60;
    	var lunch_time = time3[0] / 60;
    	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
    	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
        var num = dif;
        // console.log(num);
        var hours = (num / 60);
        var rhours = Math.floor(hours);
        var minutes = (hours - rhours) * 60;
        var rminutes = Math.round(minutes);
        // console.log(rhours +":"+ rminutes +":"+'00');
        d.total_working_hours = rhours +":"+ rminutes +":"+'00'
        if(num > 480.1333333333333){
            var ghours = rhours - 8
            var gminutes = rminutes - 0 
            var ot_hours = ghours +":"+ gminutes +':00'
            d.ot = ot_hours 
        }
        else{
            d.ot = "00:00:00"
        }
    })
    
    },
})
frappe.ui.form.on('Project Day Plan Employee', {
    
    
    project_day_plan_employee_add:function(frm,cdt,cdn){
        var row = locals[cdt][cdn]
        row.project = frm.doc.project
		row.from_time = frm.doc.from_time
		row.to_time = frm.doc.to_time
    },
    
   
	// employee: function(frm,cdt,cdn){
	// 	var row = locals[cdt][cdn]
	// 	var from_time = row.from_time
	// 	var time2= from_time.split(':')
    // 	var hourInMinOfExit = time2[0] * 60;
    // 	var secondInMinOfExit = time2[0] / 60;
    // 	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    //     var num = totalMinsOfExit
    //     var hours = (num / 60);
    //     var rhours = Math.floor(hours);
    //     var minutes = (hours - rhours) * 60;
    //     var rminutes = Math.round(minutes);
    //     var ghours = rhours + 9
    //     var gminutes = rminutes + 0 
    //     var totime = ghours +":"+ gminutes +':00'
    //     console.log(totime)
    //     row.to_time = totime 
    //     // frm.trigger('to_time')
    //     var row = locals[cdt][cdn]
	// 	var to_time = row.to_time
	// 	var from_time =row.from_time
	// 	var lunch_break=row.lunch_break
		
	// 	var time1= from_time.split(':')
	// 	var time2= to_time.split(':')
	// 	var time3= lunch_break.split(':')
	// 	var hourInMinOfEntry=time1[0] * 60;
    // 	var hourInMinOfExit = time2[0] * 60;
    // 	var lunch = time3[0] * 60;
    	
    // 	var secondInMinOfEntry = time1[0] / 60;
    // 	var secondInMinOfExit = time2[0] / 60;
    // 	var lunch_time = time3[0] / 60;
    // 	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    // 	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    // 	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
    // 	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
    //     var num = dif;
    //     // console.log(num);
    //     var hours = (num / 60);
    //     var rhours = Math.floor(hours);
    //     var minutes = (hours - rhours) * 60;
    //     var rminutes = Math.round(minutes);
    //     // console.log(rhours +":"+ rminutes +":"+'00');
    //     row.total_working_hours = rhours +":"+ rminutes +":"+'00'
    //     if(num > 480.1333333333333){
    //         var ghours = rhours - 8
    //         var gminutes = rminutes - 0 
    //         var ot_hours = ghours +":"+ gminutes +':00'
    //         row.ot = ot_hours 
    //     }
    //     else{
    //         row.ot = "00:00:00"
    //     }
    //     frm.refresh_field("project_day_plan_employee")
		
    // },
    total_working_hours: function(frm,cdt,cdn){
		var row = locals[cdt][cdn]
        frappe.db.get_value('Employee', { 'employee_number': row.employee }, 'basic')
            .then(r => {
                var one_day_amount = r.message.basic / 26;
                    var value = row.total_working_hours[1];
                    var wh = one_day_amount /value;
                    row.amount = wh
                    var ot_value = row.ot[1];
                    var ot = wh * ot_value;
    
            })

		row.from_time = "06:00"
		var from_time = row.from_time
		var time2= from_time.split(':')
    	var hourInMinOfExit = time2[0] * 60;
    	var secondInMinOfExit = time2[0] / 60;
    	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
        var num = totalMinsOfExit
        var hours = (num / 60);
        var rhours = Math.floor(hours);
        var minutes = (hours - rhours) * 60;
        var rminutes = Math.round(minutes);
		var twh = row.total_working_hours
		var time3= twh.split(':')
    	var hourInMinOfExi = time3[0] * 60;
    	var secondInMinOfExi = time3[0] / 60;
    	var totalMinsOfExi=hourInMinOfExi+parseInt(time3[1]) + secondInMinOfExi;
        var num1 = totalMinsOfExi
        var hours1 = (num1 / 60);
        var rhours1 = Math.floor(hours1);
        var minutes1 = (hours1 - rhours1) * 60;
        var rminutes1 = Math.round(minutes1);
        var ot = row.ot
		var time1= ot.split(':')
    	var hourInMin = time1[0] * 60;
    	var secondInMin = time1[0] / 60;
    	var totalMins=hourInMin+parseInt(time1[1]) + secondInMin;
        var num_1 = totalMins
        var hours_1 = (num_1 / 60);
        var rhours_1 = Math.floor(hours_1);
        var minutes_1 = (hours_1 - rhours_1) * 60;
        var rminutes_1 = Math.round(minutes_1);
        var ghours = rhours + rhours1 + rhours_1
        var gminutes = rminutes + rminutes1 + rminutes_1
        var totime = ghours +":"+ gminutes +':00'
        row.to_time = totime 

        var to_time = row.to_time
		var from_time =row.from_time
		
		var time1= from_time.split(':')
		var time2= to_time.split(':')
		var hourInMinOfEntry=time1[0] * 60;
    	var hourInMinOfExit = time2[0] * 60;
    	
    	var secondInMinOfEntry = time1[0] / 60;
    	var secondInMinOfExit = time2[0] / 60;
    	var fro=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    	var to_=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;

    	var dif = to_ - fro
        var num = dif;
        var hours = (num / 60);
        var rhours = Math.floor(hours);
        var minutes = (hours - rhours) * 60;
        var rminutes = Math.round(minutes);
        if(num > 480.1333333333333){
            var ghours = rhours - 8
            var gminutes = rminutes - 0 
            var ot_hours = ghours +":"+ gminutes +':00'
            row.ot = ot_hours
        }
        else{
            row.ot = "00:00:00"
        }

        frm.refresh_field("project_day_plan_employee")		
    },
    ot: function(frm,cdt,cdn){
        var row = locals[cdt][cdn]
        frappe.db.get_value('Employee', { 'employee_number': row.employee }, 'basic')
        .then(r => {
        var one_day_amount =r.message.basic / 26;
        var value =row.total_working_hours[1]
        var wh = one_day_amount/value
        console.log(wh);
        var ot_value =row.ot[1]
        var ot = wh*ot_value
        row.amount =ot
        
        })
		row.from_time = "06:00"
		var from_time = row.from_time
		var time2= from_time.split(':')
    	var hourInMinOfExit = time2[0] * 60;
    	var secondInMinOfExit = time2[0] / 60;
    	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
        var num = totalMinsOfExit
        var hours = (num / 60);
        var rhours = Math.floor(hours);
        var minutes = (hours - rhours) * 60;
        var rminutes = Math.round(minutes);
		var twh = row.total_working_hours
		var time3= twh.split(':')
    	var hourInMinOfExi = time3[0] * 60;
    	var secondInMinOfExi = time3[0] / 60;
    	var totalMinsOfExi=hourInMinOfExi+parseInt(time3[1]) + secondInMinOfExi;
        var num1 = totalMinsOfExi
        var hours1 = (num1 / 60);
        var rhours1 = Math.floor(hours1);
        var minutes1 = (hours1 - rhours1) * 60;
        var rminutes1 = Math.round(minutes1);

        var ot = row.ot
		var time1= ot.split(':')
    	var hourInMin = time1[0] * 60;
    	var secondInMin = time1[0] / 60;
    	var totalMins=hourInMin+parseInt(time1[1]) + secondInMin;
        var num_1 = totalMins
        var hours_1 = (num_1 / 60);
        var rhours_1 = Math.floor(hours_1);
        var minutes_1 = (hours_1 - rhours_1) * 60;
        var rminutes_1 = Math.round(minutes_1);
        var ghours = rhours + rhours1 + rhours_1
        var gminutes = rminutes + rminutes1 + rminutes_1
        var totime = ghours +":"+ gminutes +':00'
        row.to_time = totime 


        

        frm.refresh_field("project_day_plan_employee")		
    },
	// from_time: function(frm,cdt,cdn){
	// 	var row = locals[cdt][cdn]
	// 	var from_time = row.from_time
	// 	var time2= from_time.split(':')
    // 	var hourInMinOfExit = time2[0] * 60;
    // 	var secondInMinOfExit = time2[0] / 60;
    // 	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    //     var num = totalMinsOfExit
    //     var hours = (num / 60);
    //     var rhours = Math.floor(hours);
    //     var minutes = (hours - rhours) * 60;
    //     var rminutes = Math.round(minutes);
    //     var ghours = rhours + 9
    //     var gminutes = rminutes + 0 
    //     var totime = ghours +":"+ gminutes +':00'
    //     console.log(totime)
    //     row.to_time = totime 
    //     // frm.trigger('to_time')
    //     var row = locals[cdt][cdn]
	// 	var to_time = row.to_time
	// 	var from_time =row.from_time
	// 	var lunch_break=row.lunch_break
		
	// 	var time1= from_time.split(':')
	// 	var time2= to_time.split(':')
	// 	var time3= lunch_break.split(':')
	// 	var hourInMinOfEntry=time1[0] * 60;
    // 	var hourInMinOfExit = time2[0] * 60;
    // 	var lunch = time3[0] * 60;
    	
    // 	var secondInMinOfEntry = time1[0] / 60;
    // 	var secondInMinOfExit = time2[0] / 60;
    // 	var lunch_time = time3[0] / 60;
    // 	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    // 	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    // 	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
    // 	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
    //     var num = dif;
    //     // console.log(num);
    //     var hours = (num / 60);
    //     var rhours = Math.floor(hours);
    //     var minutes = (hours - rhours) * 60;
    //     var rminutes = Math.round(minutes);
    //     // console.log(rhours +":"+ rminutes +":"+'00');
    //     row.total_working_hours = rhours +":"+ rminutes +":"+'00'
    //     if(num > 480.1333333333333){
    //         var ghours = rhours - 8
    //         var gminutes = rminutes - 0 
    //         var ot_hours = ghours +":"+ gminutes +':00'
    //         row.ot = ot_hours 
    //     }
    //     else{
    //         row.ot = "00:00:00"
    //     }
    //     frm.refresh_field("project_day_plan_employee")
		
    // },
	// to_time: function(frm,cdt,cdn){
	// 	var row = locals[cdt][cdn]
	// 	var to_time = row.to_time
	// 	var from_time =row.from_time
	// 	var lunch_break=row.lunch_break
		
	// 	var time1= from_time.split(':')
	// 	var time2= to_time.split(':')
	// 	var time3= lunch_break.split(':')
	// 	var hourInMinOfEntry=time1[0] * 60;
    // 	var hourInMinOfExit = time2[0] * 60;
    // 	var lunch = time3[0] * 60;
    	
    // 	var secondInMinOfEntry = time1[0] / 60;
    // 	var secondInMinOfExit = time2[0] / 60;
    // 	var lunch_time = time3[0] / 60;
    // 	var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    // 	var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    // 	var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
    // 	var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
    //     var num = dif;
    //     // console.log(num);
    //     var hours = (num / 60);
    //     var rhours = Math.floor(hours);
    //     var minutes = (hours - rhours) * 60;
    //     var rminutes = Math.round(minutes);
    //     // console.log(rhours +":"+ rminutes +":"+'00');
    //     row.total_working_hours = rhours +":"+ rminutes +":"+'00'
    //     if(num > 480.1333333333333){
    //         var ghours = rhours - 8
    //         var gminutes = rminutes - 0 
    //         var ot_hours = ghours +":"+ gminutes +':00'
    //         row.ot = ot_hours 
    //     }
    //     else{
    //         row.ot = "00:00:00"
    //     }
    //     frm.refresh_field("project_day_plan_employee")
	// },
	// lunch_break: function(frm,cdt,cdn){
	// 	var row = locals[cdt][cdn]
		// var to_time = row.to_time
		// var from_time =row.from_time
		// var lunch_break=row.lunch_break
		
		// var time1= from_time.split(':')
		// var time2= to_time.split(':')
		// var time3= lunch_break.split(':')
		// var hourInMinOfEntry=time1[0] * 60;
    	// var hourInMinOfExit = time2[0] * 60;
    	// var lunch = time3[0] * 60;
    	
    	// var secondInMinOfEntry = time1[0] / 60;
    	// var secondInMinOfExit = time2[0] / 60;
    	// var lunch_time = time3[0] / 60;
    	// var totalMinsOfEntry=hourInMinOfEntry+parseInt(time1[1]) + secondInMinOfEntry;
    	// var totalMinsOfExit=hourInMinOfExit+parseInt(time2[1]) + secondInMinOfExit;
    	// var break_for_lunch=lunch+parseInt(time3[1]) + lunch_time;
    	// var dif = totalMinsOfExit-totalMinsOfEntry-break_for_lunch
        // var num = dif;
        // // console.log(num);
        // var hours = (num / 60);
        // var rhours = Math.floor(hours);
        // var minutes = (hours - rhours) * 60;
        // var rminutes = Math.round(minutes);
        // // console.log(rhours +":"+ rminutes +":"+'00');
        // row.total_working_hours = rhours +":"+ rminutes +":"+'00'
        // if(num > 480.1333333333333){
        //     var ghours = rhours - 8
        //     var gminutes = rminutes - 0 
        //     var ot_hours = ghours +":"+ gminutes +':00'
        //     row.ot = ot_hours 
        // }
        // else{
        //     row.ot = "00:00:00"
        // }
    //     frm.refresh_field("project_day_plan_employee")
	// }
	
})

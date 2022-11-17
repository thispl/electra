frappe.ui.form.on('External Provider Evaluation Form', {
    onload: function(frm) {
		if(frm.doc.__islocal){
        frm.set_value('approved_by',frappe.session.user)
        frm.set_value('approved_date',frappe.datetime.nowdate())
        frm.set_value('date_of_evaluation',frappe.datetime.nowdate())
        frm.set_value('reevaluation_date',frappe.datetime.nowdate())
        if(frm.doc.__islocal){
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Evaluation Parameter",
				order_by: "name",
				fields: ["name"],
			},
			callback: function(r) {
				if(r.message) {
				    frm.clear_table("evaluation_ratings");
					$.each(r.message,function(i,d){
						frm.add_child("evaluation_ratings", {
							evaluation_parameter: d.name,
						})
						frm.refresh_field('evaluation_ratings');
					})
				}
			}
		});
        }
	}
	},
	before_submit(frm) {
	    var actual_score = frm.doc.actual_score
	    var maximum_score = frm.doc.maximum_score
	    var actual_percent = (actual_score / maximum_score) * 100
	    if(actual_percent < frm.doc.acceptance_criteria && frm.doc.approval_status == 'Approved'){
	        frappe.msgprint("Actual Percentage is less than the accepted Criteria")
	        frappe.validated = false
	    }
	    else if(frm.doc.approval_status == 'Approved'){
	        frappe.db.set_value('Supplier', frm.doc.external_provider, 'approved_supplier', 1)
			.then(r => {
				let doc = r.message;
			})
		}
	},
    validate(frm){
        
        if(frm.doc.actual_score > frm.doc.maximum_score){
	        frappe.msgprint("Actual Score is greater than the maximum score")
	        frappe.validated = false
	    }
        var total = 0
        $.each(frm.doc.evaluation_ratings,function(i,d){
            if(d.rating){
            total += d.rating
            }
        })
        frm.set_value('actual_score',total)
       
//    
    },
    
    
    
});	

frappe.listview_settings['Stock Request'] = {
	onload:function(me){
        frappe.db.get_list('User Permission', {
            fields: ['for_value'],
            filters: {
                "allow": 'Company'
            }
        }).then(records => {
            var companies = []
            $.each(records,function(i,d){
                companies.push(d['for_value'])
            });
            me.filter_area.add([[me.doctype, "company", 'in', companies]]);
        })
        
	}
};
